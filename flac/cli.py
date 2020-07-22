import click

import flask
import flask.cli

import flac.database


@click.command()
@click.option('--drop-first', is_flag=True, default=False)
@click.option('--for-tests', is_flag=True, default=False)
@flask.cli.with_appcontext
def db_init(drop_first, for_tests):
    """ Initialize the database """
    app = flask.current_app
    sa_url = app.config['SQLALCHEMY_DATABASE_URI']
    if for_tests:
        sa_url += '_tests'

    flac.database.create_db(sa_url, drop_first)


class FlacGroup(flask.cli.FlaskGroup):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_command(db_init)


def cli_entry(flac_app_cls):

    def inner(wrapped):
        wrapped = flask.cli.pass_script_info(wrapped)
        wrapped = click.option('--quiet', 'log_level', flag_value='quiet',
            help='Hide info level log messages')(wrapped)
        wrapped = click.option('--info', 'log_level', flag_value='info', default=True,
            help='Show info level log messages (default)')(wrapped)
        wrapped = click.option('--debug', 'log_level', flag_value='debug',
            help='Show debug level log messages')(wrapped)
        return click.group(cls=FlacGroup,
            create_app=lambda _: flac_app_cls.create(init_app=False))(wrapped)

    return inner
