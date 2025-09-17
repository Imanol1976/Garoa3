import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
          host='127.0.0.1',      #  host='tu_host',
          user='imanol',           #  user='tu_usuario',
          password='urrestilla',   #  password='tu_contraseña',
          database='garoa_db' ,   # database='tu_base_de_datos'
          charset = 'utf8mb4',  # Establece el charset
          collation = 'utf8mb4_unicode_ci'  # Establece la collation
    )

    cursor = conn.cursor()
    cursor.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';")
    cursor.close()
    return conn