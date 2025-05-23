import datetime as dt
import logging

from pythonjsonlogger import json as jsonlogger


log = logging.getLogger(__name__)

LOG_STDOUT_FORMAT_STR_INFO = '%(message)s'
LOG_STDOUT_FORMAT_STR_DEBUG = '%(levelname)s - %(name)s - %(message)s'


def init_logging(level, appname):
    root_logger = logging.getLogger()

    minimum_level = logging.DEBUG if level == 'debug' else logging.INFO
    root_logger.setLevel(minimum_level)

    init_stdout_logging(root_logger, level)


def init_stdout_logging(logger, level):
    # always show warnings and exceptions
    error_handler = logging.StreamHandler()
    error_handler.setFormatter(logging.Formatter(LOG_STDOUT_FORMAT_STR_DEBUG))
    error_handler.setLevel(logging.WARN)
    logger.addHandler(error_handler)

    if level == 'quiet':
        return

    handler = logging.StreamHandler()
    logger.addHandler(handler)

    # Because we have a handler above that will show warnings and exceptions, this handler
    # should only show messages below those levels or we will get duplicate messages.
    handler.addFilter(BelowWarnings())

    if level == 'info':
        handler.setFormatter(logging.Formatter(LOG_STDOUT_FORMAT_STR_INFO))
        handler.setLevel(logging.INFO)
    elif level == 'debug':
        handler.setFormatter(logging.Formatter(LOG_STDOUT_FORMAT_STR_DEBUG))
        handler.setLevel(logging.DEBUG)


class BelowWarnings(logging.Filter):
    """
    Don't report warnings or above.
    """

    def filter(self, record):
        if record.levelno < logging.WARNING:
            return True


class JSONFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        # Log processing providers like logzio often auto-recognize a field labeled "timestamp".
        log_record['timestamp'] = dt.datetime.utcnow().isoformat()
        return log_record


def create_json_formatter():
    format_str = (
        '%(pathname) %(funcName) %(lineno) %(message) %(levelname)'
        ' %(name)s %(process) %(processName) %(message)'
    )
    # @cee is recognized by logging parsers as a JSON string
    return JSONFormatter(format_str, prefix='@cee:')
