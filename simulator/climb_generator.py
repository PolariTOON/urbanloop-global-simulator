import logging
import random

from model.station import *
from settings import config
from simulator import converter


class ClimbGenerator:
    def __init__(self, env=None):
        self.stations = get_stations()
        self.env = env
        self.climbing_time = int(config.capsule['climbing_time'])

    def climb_event(self, station_name):
        climb_timeout = self.env.timeout(random_climbing_time() * (1 / float(config.sim['tick'])))
        climb_timeout.callbacks.append(lambda event: callback(event, self.env, station_name))
        yield climb_timeout

    def generate(self):
        for station in self.stations:
            if not station.traveler_queue.empty() and not station.capsule_queue.empty():
                traveler = station.traveler_queue.get_nowait()
                capsule = station.capsule_queue.get_nowait()
                logging.info("[%s] Start climb at %s" % (station.name, converter.seconds_to_string(
                    converter.now_to_seconds(self.env, float(config.sim['tick']), int(config.sim['start_hour'])))))
                yield self.env.process(self.climb_event(station.name))


def random_climbing_time():
    # TODO Utiliser une gaussienne à 8 secondes
    return random.randrange(6, 10, 1)


def callback(event, env, station_name):
    logging.info("[%s] End climb at %s" % (station_name, converter.seconds_to_string(
        converter.now_to_seconds(env, float(config.sim['tick']), int(config.sim['start_hour'])))))
