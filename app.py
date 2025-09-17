import secrets  # Para generar tokens de seguridad
import smtplib  # Para enviar correos electrónicos
from email.mime.text import MIMEText

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from centros.routes import bp as centros_bp  # Importamos el Blueprint
from database import get_db_connection
from flask_session import Session
from helpers import apology, login_required, usd
from servicios.routes import bp as servicios_bp  # Importamos el Blueprint de servicios
from servicios_limpieza.routes import bp as servicios_limpieza_bp

# Configure application 1
app = Flask(__name__)

app.register_blueprint(centros_bp, url_prefix='/centros')
app.register_blueprint(servicios_bp, url_prefix='/servicios')
app.register_blueprint(servicios_limpieza_bp, url_prefix='/servicios_limpieza')


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

import requests
# Define the function to extract token from XML response

def send_reset_email(email, reset_url):
    from_email = "pruebas.ausolan@gmail.com"
    msg = MIMEText(f"Para restablecer tu contrasena, haz clic en el siguiente enlace: {reset_url}")
    msg["Subject"] = "Restablecer contraseña"
    msg["From"] = from_email
    msg["To"] = email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, 'gfh325gm')  # Asegúrate de proteger esto adecuadamente
        server.sendmail(from_email, email, msg.as_string())

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/create_entities", methods=["GET", "POST"])
def create_entities():
    if request.method == "POST":
        # Obtener datos del formulario
        centro = request.form.get("centro")
        edificio = request.form.get("edificio")
        planta = request.form.get("planta")
        hueco = request.form.get("hueco")

        # Lógica para guardar en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Guardar el centro
        cursor.execute("INSERT INTO lugares (nombre, tipo) VALUES (?, 'centro')", (centro,))
        centro_id = cursor.lastrowid

        # Guardar el edificio
        cursor.execute("INSERT INTO lugares (nombre, tipo, parent_id) VALUES (?, 'edificio', ?)", (edificio, centro_id))
        edificio_id = cursor.lastrowid

        # Guardar la planta
        cursor.execute("INSERT INTO lugares (nombre, tipo, parent_id) VALUES (?, 'planta', ?)", (planta, edificio_id))
        planta_id = cursor.lastrowid

        # Guardar el hueco
        cursor.execute("INSERT INTO lugares (nombre, tipo, parent_id) VALUES (?, 'hueco', ?)", (hueco, planta_id))

        conn.commit()
        conn.close()

        return redirect(url_for('success'))

    return render_template("create_entities.html")

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # dictionary=True devuelve los resultados como diccionarios

        # Query para buscar el nombre de usuario
        cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),))
        rows = cursor.fetchall()
        izena = request.form.get("username")
        kontrasenia = request.form.get("password")
        print ("usuarioaren izena", izena)
        print("usuarioaren kontrasenia", kontrasenia)
        cursor.close()
        conn.close()
        print("datu basearen izena", rows[0]["username"])
        print ("datu basearen kontrasenia", rows[0]["password_hash"])
        # Ensure username exists and password is correct
        #ojo! contraseña sin cifrar
        if len(rows) != 1 or rows[0]["password_hash"] != request.form.get("password"):
            return apology("invalid username and/or password", 403)

        #if len(rows) != 1 or not check_password_hash(
        #    rows[0]["password_hash"], request.form.get("password")
        #):
        #    return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Validar que los campos no estén vacíos
        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

        # Generar el hash de la contraseña
        hash_password = generate_password_hash(password)

        # Conectar a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Intentar insertar el nuevo usuario
            cursor.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", (username, hash_password))
            conn.commit()
        except mysql.connector.IntegrityError:
            return apology("username already exists", 403)
        finally:
            cursor.close()
            conn.close()

        # Redirigir al usuario a la página de inicio de sesión
        return redirect("/login")

    else:
        # Si es un GET, mostrar el formulario de registro
        return render_template("register.html")

@app.route("/eguraldia", methods=["GET", "POST"])
@login_required
def eguraldia():
    weather = None
    lekua = None

    if request.method == "POST":
        lekua = request.form.get("lekua")
        print ("lekua: ", lekua)
        api_key = "4d711d0e5f37caf21ba460358ffb5bf5"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={lekua}&appid={api_key}&units=metric&lang=es"
        response = requests.get(url)
        print ("response: ", response)
        if response.status_code == 200:
            weather = response.json()
            print ("el tiempo: ", weather)

    return render_template("eguraldia/eguraldia.html", weather=weather, lekua=lekua)

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")

        # Verificar si el correo existe en la base de datos
        #conn = get_db_connection()
        #user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        #conn.close()
        # Verificar si el correo existe en la base de datos
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # Crear un cursor
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))  # Usar el cursor para ejecutar la consulta
        user = cursor.fetchone()  # Obtener el primer resultado
        cursor.close()  # Cerrar el cursor
        conn.close()  # Cerrar la conexión

        if user:
            # Generar un token de restablecimiento de contraseña
            token = secrets.token_urlsafe(16)

            # Aquí deberías guardar el token en la base de datos asociado al usuario
            conn = get_db_connection()
            cursor = conn.cursor()  # Crear un nuevo cursor
            cursor.execute("UPDATE users SET reset_token = %s WHERE email = %s",
                           (token, email))  # Usar el cursor para ejecutar la consulta
            conn.commit()  # Confirmar los cambios
            cursor.close()  # Cerrar el cursor
            conn.close()  # Cerrar la conexión

            # Aquí deberías guardar el token en la base de datos asociado al usuario
            #conn = get_db_connection()
            #conn.execute("UPDATE users SET reset_token = ? WHERE email = ?", (token, email))
            #conn.commit()
            #conn.close()

            # Enviar el correo electrónico con el enlace para restablecer la contraseña
            reset_url = url_for('reset_password', token=token, _external=True)
            print ('email: ',email)
            print ('reset_url: ',reset_url)
            send_reset_email(email, reset_url)

            flash("Se ha enviado un enlace de restablecimiento de contraseña a tu correo.")
            return redirect(url_for('login'))
        else:
            flash("Correo no encontrado.")
            return redirect(url_for('forgot_password'))

    return render_template("forgot_password.html")

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        password = request.form.get("password")
        hash_password = generate_password_hash(password)

        # Actualizar la nueva contraseña en la base de datos
        conn = get_db_connection()
        conn.execute("UPDATE users SET password_hash = ?, reset_token = NULL WHERE reset_token = ?", (hash_password, token))
        conn.commit()
        conn.close()

        flash("Tu contraseña ha sido restablecida correctamente.")
        return redirect(url_for('login'))

    return render_template("reset_password.html", token=token)

if __name__ == "__main__":
    app.run(debug=True,  port=8080)
