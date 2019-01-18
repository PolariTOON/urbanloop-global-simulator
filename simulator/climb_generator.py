import logging

from model.station import *
from settings import config
from simulator import converter


class ClimbGenerator:
    def __init__(self, env=None):
        self.stations = get_stations()
        self.env = env
        self.climbing_time = int(config.capsule['climbing_time'])

    def timeout_event(self):
        test = random_climbing_time() * (1 / float(config.sim['tick']))
        return self.env.timeout(test)

    def climb(self):
        for station in self.stations:
            if station is not None and station.traveler_queue.qsize() > 0 and station.capsule_queue.qsize() > 0:
                traveler = station.traveler_queue.get()
                capsule = station.capsule_queue.get()
                logging.info("Traveler climb at time %s" % converter.seconds_to_string(
                    converter.now_to_seconds(self.env, float(config.sim['tick']), int(config.sim['start_hour']))))
                yield self.timeout_event()
        yield self.timeout_event()


def random_climbing_time():
    # TODO Utiliser une gaussienne à 8 secondes
    return 4
