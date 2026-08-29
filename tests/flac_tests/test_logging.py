import logging
from unittest import mock

import pytest

import flac.logging


class TestInitLogging:
    @pytest.fixture()
    def loggers(self):
        root_logger = logging.getLogger()
        app_logger = logging.getLogger('flac-test-app')
        original_root_level = root_logger.level
        original_app_level = app_logger.level

        yield root_logger, app_logger

        root_logger.setLevel(original_root_level)
        app_logger.setLevel(original_app_level)

    def test_debug_applies_to_app(self, loggers):
        root_logger, app_logger = loggers

        with mock.patch.object(flac.logging, 'init_stdout_logging') as init_stdout_logging:
            flac.logging.init_logging('debug', 'flac-test-app')

        assert root_logger.level == logging.INFO
        assert app_logger.level == logging.DEBUG
        init_stdout_logging.assert_called_once_with(root_logger, 'debug')

    def test_debug_root_applies_to_root(self, loggers):
        root_logger, app_logger = loggers

        with mock.patch.object(flac.logging, 'init_stdout_logging') as init_stdout_logging:
            flac.logging.init_logging('debug-root', 'flac-test-app')

        assert root_logger.level == logging.DEBUG
        assert app_logger.level == logging.NOTSET
        init_stdout_logging.assert_called_once_with(root_logger, 'debug')
