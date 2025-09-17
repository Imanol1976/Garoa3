from flask import Blueprint

bp = Blueprint('centros', __name__)

from . import routes
