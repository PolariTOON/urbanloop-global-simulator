import logging

from model import loop
from model import station
from model import switch
from simulator import converter

_loaded = False


def _load():
    global _loaded
    _loaded = True


def _format(message, *elements):
    time_string = converter.seconds_to_string(converter.now_to_seconds())
    elements_string = None

    for element in elements:
        element_name = element

        if type(element) in (station.Station, switch.Switch):
            element_name = element.name
        elif type(element) is loop.Loop:
            element_name = 'Loop:' + element.name
        elif type(element) is not str:
            continue

        if elements_string is None:
            elements_string = element_name
        else:
            elements_string += '->' + element_name

    if elements_string is not None:
        return "[%s][%s] %s" % (time_string, elements_string, message)

    return "[%s] %s" % (time_string, message)


def debug(message, *stations_switches_loops_or_strings):
    logging.debug(_format(message, *stations_switches_loops_or_strings))


def info(message, *stations_switches_loops_or_strings):
    logging.info(_format(message, *stations_switches_loops_or_strings))


def warn(message, *stations_switches_loops_or_strings):
    logging.warning(_format(message, *stations_switches_loops_or_strings))


def error(message, *stations_switches_loops_or_strings):
    logging.error(_format(message, *stations_switches_loops_or_strings))


if _loaded is False:
    _load()
    logging.basicConfig(format='[%(levelname)s]%(message)s', level=logging.ERROR)
