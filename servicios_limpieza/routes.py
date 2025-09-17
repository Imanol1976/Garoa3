from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db_connection

bp = Blueprint('servicios_limpieza', __name__)

# Ruta para la lista de servicios de limpieza con filtros y paginación
@bp.route('/', methods=['GET'])
def index():
    # Obtener parámetros de filtro
    nombre = request.args.get('nombre', '').strip()
    descripcion = request.args.get('descripcion', '').strip()

    # Parámetros de paginación
    page = request.args.get('page', 1, type=int)  # Página actual, por defecto 1
    per_page = 5  # Número de servicios por página (puedes ajustarlo)

    # Conectar a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Construir la consulta con filtros
    query = 'SELECT * FROM servicios WHERE tipo_servicio_id = 4 AND nombre LIKE %s AND descripcion LIKE %s LIMIT %s OFFSET %s'
    cursor.execute(query, (f'%{nombre}%', f'%{descripcion}%', per_page, (page - 1) * per_page))

    servicios_limpieza = cursor.fetchall()
    #print ("servicios_limpieza = " ,servicios_limpieza)
    # Obtener el total de resultados para la paginación
    cursor.execute('SELECT COUNT(*) FROM servicios WHERE tipo_servicio_id = 4 AND nombre LIKE %s AND descripcion LIKE %s', (f'%{nombre}%', f'%{descripcion}%'))
    total_servicios = cursor.fetchone()['COUNT(*)']

    cursor.close()
    conn.close()

    # Calcular el total de páginas
    total_paginas = (total_servicios + per_page - 1) // per_page  # Redondeo hacia arriba

    # Pasar todas las variables necesarias a la plantilla
    return render_template('servicios_limpieza/index2.html', servicios=servicios_limpieza, nombre=nombre, descripcion=descripcion,
                           page=page, total_paginas=total_paginas)

