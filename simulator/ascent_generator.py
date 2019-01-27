import logging
import random

from model.station import *
from settings import config


class ClimbGenerator:
    def __init__(self, env=None):
        self.stations = get_stations()
        self.env = env
        self.climbing_time = int(config.capsule['climbing_time'])
        self.tick_per_second = (1 / float(config.sim['tick']))

    def ascent_event(self, capsule):
        climb_timeout = self.env.timeout(random_ascent_duration() * self.tick_per_second)
        climb_timeout.callbacks.append(lambda event: ascent_event_callback(event=event, capsule=capsule))
        yield climb_timeout

    def generate(self):
        for station in self.stations:
            if not station.traveler_queue.empty() and not station.capsule_queue.empty():
                traveler = station.traveler_queue.get_nowait()
                capsule = station.capsule_queue.get_nowait()
                capsule.get_in_traveler(traveler=traveler)
                yield self.env.process(self.ascent_event(capsule))


def random_ascent_duration():
    return random.randrange(6, 10, 1)


def ascent_event_callback(event, capsule):
    logging.info("Capsule %d starts its trip" % capsule.id)
