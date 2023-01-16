import logging

import click
from flask import Blueprint, current_app


log = logging.getLogger(__name__)
cli_bp = Blueprint('cli', __name__, cli_group=None)


@cli_bp.cli.command()
@click.argument('name', default='World')
def hello(name):
    log.debug('cli debug logging example')
    print(f'Hello, {name}!')


@cli_bp.cli.command()
@click.argument('bind', default='127.0.0.1:5000')
@click.option('--workers', default=3)
def gunicorn(bind, workers):
    """ Run app with gunicorn

        In production, set FLASK_ENV=production
    """
    # Keep import inside function to avoid needing gunicorn installed
    # unless it's going to be used.
    from flac.contrib.gunicorn import AppServer

    # Add the options you need, see:
    # https://docs.gunicorn.org/en/latest/settings.html
    opts = dict(bind=bind, workers=workers)

    app = current_app._get_current_object()
    print('Flask app environment is:', app.env)
    AppServer(app, opts).run()
