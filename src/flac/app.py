import logging
import pathlib
from typing import Self

import flask

from . import testing
from .config import init_config
from .logging import init_logging


log = logging.getLogger(__name__)


class FlacApp(flask.Flask):
    test_cli_runner_class = testing.CLIRunner

    @classmethod
    def create(cls, app_name, root_path, init_app=True, testing=False, **kwargs) -> Self:
        """
        For CLI app init blueprints but not config b/c we want to give the calling CLI group
        the ability to set values from the command line args/options before configuring the
        app. But if we don't init the blueprints right away, then the CLI doesn't know
        anything about the cli groups & commands added by blueprints.
        """
        # Ensure a pathlib object so it can be assumed elsewhere
        root_path = pathlib.Path(root_path)

        app = cls(app_name, root_path=root_path, **kwargs)
        app.testing = testing

        app.init_blueprints()
        if init_app:
            app.init_app(None)

        return app

    def init_blueprints(self):
        pass

    def init_app(self, config_profile, log_level='info', with_sentry=False):
        init_config(self, config_profile)

        if not self.testing:
            init_logging(log_level, self.name)

        # TODO: this shouldn't be in the core
        if with_sentry:
            from flac.contrib.sentry import init_sentry

            init_sentry(self)

        self.on_app_ready()

        if self.testing:
            self.on_testing_start()

    def on_app_ready(self):
        pass

    def on_testing_start(self):
        sa_inst = self.extensions.get('sqlalchemy')
        if sa_inst:
            with self.app_context():
                sa_inst.drop_all()
                sa_inst.create_all()
