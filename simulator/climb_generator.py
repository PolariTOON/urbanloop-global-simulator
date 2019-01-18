from random import random

from model.station import *
from settings import config


class ClimbGenerator:
    def __init__(self, env=None):
        self.stations = get_stations()
        self.env = env
        self.climbing_time = int(config.capsule['climbing_time'])

    def timeout_event(self):
        return self.env.timeout(random_climbing_time() * (1 / float(config.sim['tick'])))

    def climb(self, station=None):
        traveler = station.traveler_queue.get()
        capsule = station.traveler_queue.get()
        yield self.timeout_event()

    def generate_climb(self):
        for station in self.stations:
            self.env.process(self.climb(station=station))
        yield self.env.timeout(1)


def random_climbing_time():
    # TODO Utiliser une gaussienne à 8 secondes
    return random.randint(4, 12)
