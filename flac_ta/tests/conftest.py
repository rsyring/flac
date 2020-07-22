import pytest

from flac_ta.app import App as _App
from flac_ta.ext import db as _db


@pytest.fixture(scope='session')
def App():
    return _App


@pytest.fixture(scope='session')
def app(App):
    app = App.create_test_app()

    _db.drop_all(app=app)
    _db.create_all(app=app)

    return app


@pytest.fixture(scope='session')
def script_args():
    return ['python', '-c', 'from flac_ta import app; app.cli()']


@pytest.fixture()
def db(app):
    with app.app_context():
        yield _db
        _db.session.remove()


@pytest.fixture()
def client(app):
    return app.test_client()
