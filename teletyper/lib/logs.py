from logging import (
    DEBUG, ERROR, INFO, WARNING, Formatter, StreamHandler, getLogger
)
from logging.handlers import RotatingFileHandler

from teletyper.lib import APP_NAME
from teletyper.lib.disk import join_location

LOG_LEVEL = dict(debug=DEBUG, error=ERROR, info=INFO, warning=WARNING)


def log_setup(handler, formatter, level):
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def logger(name, log_folder, log_level):
    log = getLogger()
    formatter = Formatter('''
%(levelname)s - %(asctime)s | %(name)s | %(processName)s %(threadName)s
%(module)s.%(funcName)s [%(pathname)s:%(lineno)d]
    %(message)s
'''.lstrip())
    level = LOG_LEVEL.get(log_level, INFO)
    file_size = 10 * (1024 * 1024)

    log.setLevel(DEBUG)
    log.addHandler(log_setup(StreamHandler(stream=None), formatter, level))
    log.addHandler(log_setup(RotatingFileHandler(
        join_location(log_folder, '{}_{}.log'.format(APP_NAME, log_level)),
        maxBytes=file_size, backupCount=9
    ), formatter, level))

    if level != DEBUG:
        log.addHandler(log_setup(RotatingFileHandler(
            join_location(log_folder, '{}_debug.log'.format(APP_NAME)),
            maxBytes=file_size, backupCount=4
        ), formatter, DEBUG))

    return getLogger(name)
