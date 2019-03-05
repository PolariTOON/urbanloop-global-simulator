from model import station
from settings import config, simlog
from simulator import converter
from simulator import sim_loop


class AscentGenerator:
    def __init__(self):
        self.stations = station.get_stations()
        self.trip_limit = int(config.sim['trip_limit'])

    def generate(self):
        for a_station in self.stations:
            if not a_station.traveler_queue.is_empty() and not a_station.capsule_queue.is_empty() and self.can_generate():
                if self.trip_limit != -1:
                    self.trip_limit -= 1
                traveler = a_station.traveler_queue.get()

                capsule = a_station.capsule_queue.get()
                capsule.get_in_traveler(traveler=traveler)
                yield sim_loop.get_env().process(ascent_event(capsule))

    def can_generate(self):
        return self.trip_limit > 0 or self.trip_limit == -1


def ascent_event(capsule):
    climb_timeout = sim_loop.get_env().timeout(converter.random_ascent_descent_duration())
    climb_timeout.callbacks.append(lambda event: capsule.start_trip())
    yield climb_timeout
