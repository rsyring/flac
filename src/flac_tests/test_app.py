from unittest import mock

import click
import flask

from flac.app import FlacApp


cli_bp = flask.Blueprint('cli', __name__, cli_group=None)


@cli_bp.cli.command()
@click.argument('name', default='World')
def hello(name):
    print(f'Hello {name}!')


class HelloApp(FlacApp):
    @classmethod
    def create(cls, **kwargs):
        return super().create('hello', '/fake/dir', **kwargs)

    def init_blueprints(self):
        self.register_blueprint(cli_bp)

    def on_app_ready(self):
        self._init_extensions = True
        self.extensions['sqlalchemy'] = mock.Mock()


class TestApp:
    def test_create(self):
        """create inits by default and doesn't set testing"""
        app = HelloApp.create(config_profile='foo')
        assert not app.testing

        # Make sure init_app() is called, which inits config, which sets this default value
        # TODO: could use a mock so that we are just testing init_app() method is called
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

    def test_create_testing(self):
        """testing sets testing"""
        app = HelloApp.create(testing=True)
        assert app.testing

    def test_create_app_init_false(self):
        """blueprints should be init'd, but not the rest of the app"""
        app = HelloApp.create(init_app=False)
        runner = app.test_cli_runner()

        result = runner.invoke('hello')
        assert result.output == 'Hello World!\n'

        assert app.config.get('SQLALCHEMY_TRACK_MODIFICATIONS') is None

    def test_on_app_ready_called(self):
        """make sure on app ready gets called"""
        app = HelloApp.create(testing=True)
        assert app._init_extensions

    def test_testing_drop_and_create_db(self):
        """prep the db if flask_sqlalchemy has been initialized"""
        app = HelloApp.create(testing=True)
        mock = app.extensions['sqlalchemy']
        mock.drop_all.assert_called_once_with()
        mock.create_all.assert_called_once_with()
