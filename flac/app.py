import logging
import os
import pathlib

import flask

from . import testing
from .config import init_config
from .logging import init_logging

log = logging.getLogger(__name__)


class FlacApp(flask.Flask):
    test_cli_runner_class = testing.CLIRunner
    flask_sqlalchemy_cls = None

    @classmethod
    def create(cls, app_name, root_path, init_app=True, testing=False, **kwargs):
        """
            For CLI app init blueprints but not config b/c we want to give the calling CLI group
            the ability to set values from the command line args/options before configuring the
            app. But if we don't init the blueprints right away, then the CLI doesn't know
            anything about the cli groups & commands added by blueprints.
        """
        if testing:
            os.environ['FLASK_ENV'] = 'testing'

        # Ansure a pathlib object so we can assume that elsewhere
        root_path = pathlib.Path(root_path)

        app = cls(app_name, root_path=root_path, **kwargs)
        app.testing = testing

        app.init_blueprints()
        if init_app:
            app.init_app()

        return app

    def init_blueprints(self):
        pass

    def init_app(self, log_level='info', with_sentry=False):
        init_config(self)

        if not self.testing:
            init_logging(log_level, self.name)

        if with_sentry:
            from flac.contrib.sentry import init_sentry
            init_sentry(self)

        self.on_app_ready()

        if self.testing:
            self.on_testing_start()

    def on_app_ready(self):
        pass

    def on_testing_start(self):
        fsa_state = self.extensions.get('sqlalchemy')
        if fsa_state:
            fsa_state.db.drop_all(app=self)
            fsa_state.db.create_all(app=self)
