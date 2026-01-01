from flask import Blueprint

# Define o blueprint unificado
bp = Blueprint('portfolios', __name__, url_prefix='/api/portfolios')

from . import routes
