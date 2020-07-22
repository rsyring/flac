import pathlib

import click
import flac.app
import flac.cli

import jax.cli
import jax.ext
import jax.views

app_dpath = pathlib.Path(__file__).parent


class JaxApp(flac.app.FlacApp):
    @classmethod
    def create(cls, **kwargs):
        return super().create('jax', app_dpath, **kwargs)

    def init_blueprints(self):
        self.register_blueprint(jax.cli.cli_bp)
        self.register_blueprint(jax.views.public)

    def on_app_ready(self):
        jax.ext.init_ext(self)


@flac.cli.cli_entry(JaxApp)
@click.option('--with-sentry', is_flag=True, default=False,
    help='Enable Sentry (usually only in production)')
def cli(scriptinfo, log_level, with_sentry):
    app = scriptinfo.load_app()
    app.init_app(log_level, with_sentry=with_sentry)
