import random

from model import station
from settings import config
from simulator import sim_loop


class AscentGenerator:
    def __init__(self):
        self.stations = station.get_stations()
        self.ascent_time = int(config.capsule['ascent_time'])
        self.trip_limit = int(config.sim['trip_limit'])

    def ascent_event(self, capsule):
        climb_timeout = sim_loop.get_env().timeout(self.random_ascent_duration() * sim_loop.get_tick_per_second())
        climb_timeout.callbacks.append(lambda event: capsule.start_trip())
        yield climb_timeout

    def generate(self):
        for a_station in self.stations:
            if not a_station.traveler_queue.empty() and not a_station.capsule_queue.empty() and self.can_generate():
                if self.trip_limit != -1:
                    self.trip_limit -= 1
                traveler = a_station.traveler_queue.get_nowait()
                capsule = a_station.capsule_queue.get_nowait()
                capsule.get_in_traveler(traveler=traveler)
                yield sim_loop.get_env().process(self.ascent_event(capsule))

    def can_generate(self):
        return self.trip_limit > 0 or self.trip_limit == -1

    def random_ascent_duration(self):
        return random.randrange(self.ascent_time - 2, self.ascent_time + 2, 1)
