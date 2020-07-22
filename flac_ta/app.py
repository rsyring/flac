from pathlib import Path

from flac.app import app_create

from .cli import cli_bp
from .ext import init_app
from .web import public_bp

app_dpath = Path(__file__).parent

App, cli = app_create(
    __name__.split('.')[0],
    blueprints=[
        cli_bp,
        public_bp,
    ],
    root_path=app_dpath,
    post_init=init_app,
)

App.app_dpath = app_dpath
App.project_dpath = App.app_dpath.parent
