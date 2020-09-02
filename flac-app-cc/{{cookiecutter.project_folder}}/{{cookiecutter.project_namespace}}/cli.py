import logging

import click
from flask import Blueprint


log = logging.getLogger(__name__)
cli_bp = Blueprint('cli', __name__, cli_group=None)


@cli_bp.cli.command()
@click.argument('name', default='World')
def hello(name):
    log.debug('cli debug logging example')
    print(f'Hello, {name}!')
