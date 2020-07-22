import pytest

import jax.app
import jax.ext


@pytest.fixture(scope='session')
def app():
    app = jax.app.JaxApp.create(testing=True)
    return app


@pytest.fixture()
def db(app):
    with app.app_context():
        yield jax.ext.db
        jax.ext.db.session.remove()


@pytest.fixture()
def web(app):
    return app.test_client()


@pytest.fixture()
def cli(app):
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def script_args():
    return ['python', '-c', 'from jax import app; app.cli()']
