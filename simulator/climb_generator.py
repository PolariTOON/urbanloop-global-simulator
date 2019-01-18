from model.station import *
from settings import config


class ClimbGenerator:
    def __init__(self, env=None):
        self.stations = get_stations()
        self.env = env
        self.climbing_time = int(config.capsule['climbing_time'])

    def timeout_event(self):
        event = self.env.timeout(random_climbing_time() * (1 / float(config.sim['tick'])))
        event.callbacks.append(callback)
        yield event

    def climb(self):
        for station in self.stations:
            if not station.traveler_queue.empty() and not station.capsule_queue.empty():
                traveler = station.pop_traveler()
                capsule = station.pop_capsule()
                yield self.env.process(self.timeout_event())
        yield self.env.event().succeed()


def random_climbing_time():
    # TODO Utiliser une gaussienne à 8 secondes
    return 2


def callback(event):
    print("callback")
