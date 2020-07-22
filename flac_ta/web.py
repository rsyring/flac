from flask import Blueprint

public_bp = Blueprint('public', __name__)


@public_bp.route('/hello')
def hello():
    return 'Hello World!'
