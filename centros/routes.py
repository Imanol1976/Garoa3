from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db_connection

bp = Blueprint('centros', __name__)

# Ruta para la lista de centros con filtros y paginación
@bp.route('/', methods=['GET'])
def index():
    # Obtener parámetros de filtro
    nombre = request.args.get('nombre', '').strip()
    localidad = request.args.get('localidad', '').strip()

    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)  # Página actual, por defecto 1
    per_page = 5  # Número de centros por página (puedes ajustarlo)

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Construir la consulta con filtros
    query = 'SELECT * FROM centros WHERE nombre LIKE %s AND localidad LIKE %s LIMIT %s OFFSET %s'
    cursor.execute(query, (f'%{nombre}%', f'%{localidad}%', per_page, (page - 1) * per_page))

    centros = cursor.fetchall()

    # Obtener el total de resultados para la paginación
    cursor.execute('SELECT COUNT(*) FROM centros WHERE nombre LIKE %s AND localidad LIKE %s', (f'%{nombre}%', f'%{localidad}%'))
    total_centros = cursor.fetchone()['COUNT(*)']

    cursor.close()
    conn.close()

    # Calcular el total de páginas
    total_paginas = (total_centros + per_page - 1) // per_page  # Redondeo hacia arriba

    # Pasar todas las variables necesarias a la plantilla
    return render_template('centros/index.html', centros=centros, nombre=nombre, localidad=localidad)
         #                 ,page=page, total_paginas=total_paginas)

# Ruta para agregar un nuevo centro
@bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        nombre = request.form['nombre']
        localidad = request.form['localidad']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        email = request.form['email']
        cp = request.form['cp']
        provincia_id = request.form['provincia_id']

        # Validación básica de los campos
        if not nombre or not localidad:
            return redirect(url_for('centros.add'))

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar el nuevo centro en la base de datos
        cursor.execute('''INSERT INTO centros (nombre, localidad, telefono, direccion, email, cp, provincia_id)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                       (nombre, localidad, telefono, direccion, email, cp, provincia_id))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('centros.index'))

    return render_template('centros/add.html')

# Ruta para eliminar un centro
@bp.route('/delete/<int:centro_id>', methods=['POST'])
def delete(centro_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Eliminar el centro con el ID proporcionado
    cursor.execute('DELETE FROM centros WHERE id = %s', (centro_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('centros.index'))

# Ruta para editar un centro
@bp.route('/edit/<int:centro_id>', methods=['GET', 'POST'])
def edit(centro_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Si es un GET, mostramos el formulario con los datos actuales del centro
    if request.method == 'GET':
        cursor.execute('SELECT * FROM centros WHERE id = %s', (centro_id,))
        centro = cursor.fetchone()

        # Obtener los servicios asociados al centro
       # cursor.execute('SELECT * FROM servicios WHERE centro_id = %s ', (centro_id,))
        cursor.execute('SELECT ser.*, ts.nombre as nombre_tipo FROM servicios ser left join tipos_servicios ts on ser.tipo_servicio_id = ts.id where ser.centro_id = %s ', (centro_id,))
        servicios = cursor.fetchall()

        cursor.close()
        conn.close()
#        return render_template('centros/edit.html', centro=centro)
        return render_template('centros/edit.html', centro=centro, servicios=servicios)
    # Si es un POST, actualizamos el centro con el nuevo nombre y datos
    if request.method == 'POST':
        nombre = request.form['nombre']
        localidad = request.form['localidad']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        email = request.form['email']
        cp = request.form['cp']
        provincia_id = request.form['provincia_id']

        cursor.execute('''UPDATE centros SET nombre = %s, localidad = %s, telefono = %s, direccion = %s, 
                          email = %s, cp = %s, provincia_id = %s WHERE id = %s''',
                       (nombre, localidad, telefono, direccion, email, cp, provincia_id, centro_id))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('centros.index'))
