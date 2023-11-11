import pathlib
import sys

import click
import flask
import flask.cli

import flac.config
try:
    import flac.database as flac_db
except ImportError:
    flac_db = None


@click.group()
def db():
    """ database commands """
    if not flac_db:
        message = click.style('ERROR:', fg='red')
        message += (
            ' flac.database can not be imported.  Have you uncommented and installed the'
            ' database dependencies in common.in?'
        )
        click.echo(message, err=True)
        sys.exit(1)


@db.command('init')
@click.option('--drop-first', is_flag=True, default=False)
@flask.cli.with_appcontext
def db_init(drop_first):
    """ Create databases """
    app = flask.current_app
    sa_url = app.config['SQLALCHEMY_DATABASE_URI']
    flac.database.create_db(sa_url, drop_first)


@db.command('create-all')
@flask.cli.with_appcontext
def db_create_all():
    """ Create new db objects """
    flask.current_app.extensions['sqlalchemy'].db.create_all()
    print('New database objects created')


@click.command()
@flask.cli.with_appcontext
def config_info():
    """ Show config info """
    app = flask.current_app
    print(f'app.name: {app.name}')
    print(f'app.debug: {app.debug}')
    print(f'app.testing: {app.testing}')

    print('Config file paths:')
    for fpath in flac.config.app_config_fpaths(app):
        fpath = pathlib.Path(fpath)
        status = 'exists' if fpath.exists() else 'missing'
        print(f'    {fpath}: {status}')


class FlacGroup(flask.cli.FlaskGroup):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_command(db)
        self.add_command(config_info)


def cli_entry(flac_app_cls):

    def inner(wrapped):
        wrapped = flask.cli.pass_script_info(wrapped)
        wrapped = click.option('--log-quiet', 'log_level', flag_value='quiet',
            help='Hide info level log messages')(wrapped)
        wrapped = click.option('--log-info', 'log_level', flag_value='info', default=True,
            help='Show info level log messages (default)')(wrapped)
        wrapped = click.option('--log-debug', 'log_level', flag_value='debug',
            help='Show debug level log messages')(wrapped)
        wrapped = click.option('--config-profile',
            help='Name of configuration profile to load')(wrapped)
        return click.group(cls=FlacGroup,
            create_app=lambda: flac_app_cls.create(init_app=False))(wrapped)

    return inner
