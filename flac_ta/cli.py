import logging

import click
import flask

log = logging.getLogger(__name__)

cli_bp = flask.Blueprint('cli', __name__, cli_group=None)


@cli_bp.cli.command()
@click.argument('name', default='World')
def hello(name):
    print(f'Hello {name}!')


@cli_bp.cli.command('log')
def _log():
    """ Test log message output """
    log.debug('debug log message')
    log.info('info log message')
    log.warning('warning log message')


if __name__ == '__main__':
    cli()
