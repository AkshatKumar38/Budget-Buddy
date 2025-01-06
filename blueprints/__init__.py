from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')
main_bp = Blueprint('main',__name__, url_prefix='/main')