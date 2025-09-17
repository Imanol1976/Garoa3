from flask import Blueprint

bp = Blueprint('servicios_limpieza', __name__)

from . import routes
