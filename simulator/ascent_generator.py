from model import station
from settings import config
from simulator import converter
from simulator import sim_loop


class AscentGenerator:
    def __init__(self):
        self.stations = station.get_stations()
        self.trip_limit = int(config.traveler['trip_limit'])

    def generate(self):
        for a_station in self.stations:
            if not a_station.traveler_queue.is_empty() and not a_station.capsule_queue.is_empty() and self.can_generate():
                if self.trip_limit != -1:
                    self.trip_limit -= 1
                if a_station.capsule_queue.items[0].is_aboard():
                    return

                traveler = a_station.traveler_queue.get()
                capsule = a_station.capsule_queue.get_no_pop()
                capsule.get_in_traveler(traveler=traveler)
                sim_loop.recorder.add_waiting_time_traveler(traveler.get_waiting_seconds(), traveler)
                yield sim_loop.get_env().process(ascent_event(a_station, capsule))

    def can_generate(self):
        return self.trip_limit > 0 or self.trip_limit == -1


def ascent_event(a_station, capsule):
    ascent_timeout = sim_loop.get_env().timeout(converter.random_ascent_descent_duration())
    ascent_timeout.callbacks.append(lambda event: ascent_event_callback(a_station, capsule))
    yield ascent_timeout


def ascent_event_callback(a_station, capsule):
    a_station.capsule_queue.remove(capsule)
    capsule.start_trip()
