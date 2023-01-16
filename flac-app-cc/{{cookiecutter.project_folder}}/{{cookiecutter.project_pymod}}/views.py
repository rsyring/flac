from flask import Blueprint

public = Blueprint('public', __name__)


@public.route('/')
def index():
    return 'Hello World!'


@public.route('/error')
def error():
    raise Exception('deliberate error')
