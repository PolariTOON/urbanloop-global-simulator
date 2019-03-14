import random
from math import floor

from model import station
from model import traveler
from settings import config
from settings import simlog
from simulator import converter
from simulator import poisson
from simulator import sim_loop


class TravelerGenerator:
    def __init__(self):
        self.poisson = poisson.Poisson()
        self.traveler_limit = int(config.traveler['traveler_limit'])

    def can_generate(self):
        return self.traveler_limit > 0 or self.traveler_limit == -1

    def generate(self):
        """
        :return: The generator of one or several travelers each second
        """
        seconds = converter.now_to_seconds()
        hour = converter.seconds_to_floor_hour(seconds)
        traveler_number = self.poisson.traveler(hour)
        for a_traveler in range(traveler_number):
            if not self.can_generate():
                return
            if self.traveler_limit != -1:
                self.traveler_limit -= 1

            departure_station = _select_random_station()
            destination_station = _select_random_station(departure_station=departure_station)
            traveler.Traveler(departure_station, destination_station)
            simlog.info("Traveler generated", departure_station, destination_station)
            yield sim_loop.get_env().timeout(floor(sim_loop.get_tick_per_second() / traveler_number))


def _select_random_station(departure_station=None):
    """
    If departure_station is None, it means that you are looking for
    a random departure_station. Otherwise, it means that you are
    looking for a destination_station.
    """
    is_arrival = departure_station is not None

    second = converter.now_to_seconds()
    city_prob = converter.station_probability(station.Type.CITY, second, is_arrival=is_arrival)
    residential_prob = converter.station_probability(station.Type.RESIDENTIAL, second, is_arrival=is_arrival)
    activity_prob = converter.station_probability(station.Type.ACTIVITY, second, is_arrival=is_arrival)

    prob = random.uniform(0, 1)
    interval = [0, city_prob]

    if interval[0] <= prob < interval[1]:
        return _get_random_station_from_type(station.Type.CITY, departure_station=departure_station)

    interval[0] = interval[1]
    interval[1] += residential_prob

    if interval[0] <= prob < interval[1]:
        return _get_random_station_from_type(station.Type.RESIDENTIAL, departure_station=departure_station)

    interval[0] = interval[1]
    interval[1] += activity_prob

    if interval[0] <= prob < interval[1]:
        return _get_random_station_from_type(station.Type.ACTIVITY, departure_station=departure_station)

    return _get_random_station_from_type(station.Type.CITY, departure_station=departure_station)


def _get_random_station_from_type(station_type, departure_station=None):
    """
    If departure_station is None, it means that you are looking for
    a random departure_station. Otherwise, it means that you are
    looking for a destination_station and this station can't be the
    same as the departure_station
    """

    stations = []
    for a_station in station.get_stations():
        if a_station.station_type == station_type.value:
            if departure_station is None:
                stations.append(a_station)
            elif a_station.name != departure_station.name:
                stations.append(a_station)

    if not stations:
        if departure_station is None:
            return random.choice(station.get_stations())
        else:
            return random.choice(
                [a_station for a_station in station.get_stations() if a_station.name != departure_station.name])

    return random.choice(stations)
