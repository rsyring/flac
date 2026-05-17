import click
from click.testing import CliRunner
import flask
import pytest

from flac.app import FlacApp
from flac.cli import cli_entry


@pytest.fixture(scope='module')
def cli():
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

        def init_app(self, log_level):
            print('log level:', log_level)

    @cli_entry(HelloApp)
    @click.option('--some-thing', is_flag=True, default=False)
    def cli(scriptinfo, config_profile, log_level, some_thing):
        app = scriptinfo.load_app()
        app.init_app(log_level)
        if some_thing:
            print('something')

    return cli


class TestFlacGroup:
    def test_log_level_opt(self, cli):
        result = CliRunner().invoke(cli, ['--log-quiet', 'hello'], catch_exceptions=False)
        assert 'log level: quiet' in result.output

    def test_hello_and_defaults(self, cli):
        result = CliRunner().invoke(cli, ['hello'], catch_exceptions=False)
        # the default log level
        assert 'log level: info' in result.output
        # hello output
        assert 'Hello World' in result.output
        # not on by default
        assert 'something' not in result.output

    def test_extra_option(self, cli):
        result = CliRunner().invoke(cli, ['--something', 'hello'], catch_exceptions=False)
        assert 'something' in result.output

    def test_db_init_command(self, cli):
        return
        result = CliRunner().invoke(cli, ['db', 'init', '--for-tests'], catch_exceptions=False)
        assert 'something' in result.output
