import logging

from simulator import converter

_loaded = False


def _load():
    global _loaded
    _loaded = True


def _format(message):
    return "[%s] %s" % (converter.seconds_to_string(converter.now_to_seconds()), message)


def debug(message):
    logging.debug(_format(message))


def info(message):
    logging.info(_format(message))


def warn(message):
    logging.warning(_format(message))


def error(message):
    logging.error(_format(message))


if _loaded is False:
    _load()
    logging.basicConfig(format='[%(levelname)s]%(message)s', level=logging.DEBUG)
