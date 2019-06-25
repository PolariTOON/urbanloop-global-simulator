import logging

from model import loop
from model import station
from model import switch
from settings import config
from simulator import converter


def load():
    logging.basicConfig(format='[%(levelname)s]%(message)s', level=logging.DEBUG)
    if config.sim['logs'] in ['False', 'false']:
        logging.getLogger().setLevel(logging.ERROR)
    else:
        logging.getLogger().setLevel(logging.DEBUG)

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
