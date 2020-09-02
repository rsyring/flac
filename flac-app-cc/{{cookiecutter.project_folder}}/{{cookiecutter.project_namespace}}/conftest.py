import pytest

import {{cookiecutter.project_namespace}}.app
import {{cookiecutter.project_namespace}}.ext


@pytest.fixture(scope='session')
def app():
    app = {{cookiecutter.project_namespace}}.app.{{cookiecutter.project_class}}App.create(testing=True)
    return app


@pytest.fixture()
def db(app):
    with app.app_context():
        yield {{cookiecutter.project_namespace}}.ext.db
        {{cookiecutter.project_namespace}}.ext.db.session.remove()


@pytest.fixture()
def web(app):
    return app.test_client()


@pytest.fixture()
def cli(app):
    return app.test_cli_runner()


@pytest.fixture(scope='session')
def script_args():
    return ['python', '-c', 'from {{cookiecutter.project_namespace}} import app; app.cli()']
