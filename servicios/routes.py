from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db_connection

bp = Blueprint('servicios', __name__, url_prefix='/servicios')

# Ruta para la lista de centros con filtros y paginación
@bp.route('/', methods=['GET'])
def index():
    # Obtener parámetros de filtro
    nombre = request.args.get('nombre', '').strip()
    localidad = request.args.get('localidad', '').strip()

    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)  # Página actual, por defecto 1
    per_page = 5  # Número de servicios por página (puedes ajustarlo)

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Construir la consulta con filtros
    query = 'SELECT * FROM servicios WHERE nombre LIKE %s AND localidad LIKE %s LIMIT %s OFFSET %s'
    cursor.execute(query, (f'%{nombre}%', f'%{localidad}%', per_page, (page - 1) * per_page))

    servicios = cursor.fetchall()

    # Obtener el total de resultados para la paginación
    cursor.execute('SELECT COUNT(*) FROM servicios WHERE nombre LIKE %s AND localidad LIKE %s', (f'%{nombre}%', f'%{localidad}%'))
    total_servicios = cursor.fetchone()['COUNT(*)']

    cursor.close()
    conn.close()

    # Calcular el total de páginas
    total_paginas = (total_servicios + per_page - 1) // per_page  # Redondeo hacia arriba

    # Pasar todas las variables necesarias a la plantilla
    return render_template('servicios/index2.html', centros=servicios, nombre=nombre, localidad=localidad,
                           page=page, total_paginas=total_paginas)

@bp.route('/add/<int:centro_id>', methods=['POST'])
def add(centro_id):
    servicio = Servicio(
        nombre=request.form['nombre'],
        descripcion=request.form.get('descripcion', ''),
        precio=request.form['precio'],
        fecha_desde=request.form.get('fecha_desde'),
        fecha_hasta=request.form.get('fecha_hasta'),
        tipo_servicio_id=request.form.get('tipo_servicio_id'),
        centro_id=centro_id
    )
    db.session.add(servicio)
    db.session.commit()
    flash('Servicio añadido con éxito', 'success')
    return redirect(url_for('centros.edit', centro_id=centro_id))

@bp.route('/edit/<int:servicio_id>', methods=['GET', 'POST'])
def edit(servicio_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute('SELECT * FROM servicios WHERE id = %s', (servicio_id,))
        servicio = cursor.fetchone()

        if not servicio:
            abort(404, description="Servicio no encontrado")

        # Cargar tipos de servicio para desplegar en un select2
        cursor.execute('SELECT * FROM tipos_servicios')
        tipos_servicio = cursor.fetchall()

        cursor.close()
        conn.close()

        # Verifica los datos antes de renderizar el template
        print('Tipos de servicio son: ', tipos_servicio)  # Depuración temporal

        return render_template('servicios/edit_servicios.html', servicio=servicio, tipos_servicio=tipos_servicio)

    if request.method == 'POST':
        print(request.form)
        nombre = request.form['nombre']
        tipo_servicio_id = request.form['tipo_servicio_id']
        fecha_desde = request.form['fecha_desde']
        fecha_hasta = request.form['fecha_hasta']

        cursor.execute('''
            UPDATE servicios
            SET nombre = %s, tipo_servicio_id = %s, fecha_desde = %s, fecha_hasta = %s
            WHERE id = %s
        ''', (nombre, tipo_servicio_id, fecha_desde, fecha_hasta, servicio_id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(request.referrer or url_for('centros.edit', centro_id=request.form['centro_id']))


@bp.route('/delete/<int:servicio_id>', methods=['POST'])
def delete(servicio_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    print ("hemos entrado en el delete_servicio")
    # Eliminar servicio
    cursor.execute('DELETE FROM servicios WHERE id = %s', (servicio_id,))
    conn.commit()

    cursor.close()
    conn.close()

    # Redirigir a la página de edición del centro
    return redirect(request.referrer or url_for('centros.edit'))
