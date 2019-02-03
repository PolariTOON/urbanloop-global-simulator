import random

from simulator import sim_loop  # import simulator.sim_loop as sim_loop
from model.station import get_stations
from settings import config


class AscentGenerator:
    def __init__(self):
        self.stations = get_stations()
        self.climbing_time = int(config.capsule['climbing_time'])
        self.trip_limit = int(config.sim['trip_limit'])

    def ascent_event(self, capsule):
        climb_timeout = sim_loop.get_env().timeout(self.random_ascent_duration() * sim_loop.get_tick_per_second())
        climb_timeout.callbacks.append(lambda event: capsule.start_trip())
        yield climb_timeout

    def generate(self):
        for station in self.stations:
            if not station.traveler_queue.empty() and not station.capsule_queue.empty() and self.can_generate():
                if self.trip_limit != -1:
                    self.trip_limit -= 1
                traveler = station.traveler_queue.get_nowait()
                capsule = station.capsule_queue.get_nowait()
                capsule.get_in_traveler(traveler=traveler)
                yield sim_loop.get_env().process(self.ascent_event(capsule))

    def can_generate(self):
        return self.trip_limit > 0 or self.trip_limit == -1

    def random_ascent_duration(self):
        return random.randrange(self.climbing_time - 2, self.climbing_time + 2, 1)
