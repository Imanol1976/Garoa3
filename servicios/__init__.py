from flask import Blueprint

bp = Blueprint('servicios', __name__)

from . import routes
