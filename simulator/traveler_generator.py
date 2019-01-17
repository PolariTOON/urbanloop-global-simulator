import logging
import random

from model.station import *
from model.traveler import Traveler
from settings import config
from simulator import converter
from simulator import poisson


class FlowGenerator:
    def __init__(self, env):
        self.env = env
        self.poisson = poisson.Poisson()
        self.ticks_in_second = 1 / float(config.sim['tick'])

    def generate_traveler(self, env, sim_tick, start_hour=0):
        seconds = converter.now_to_seconds(env, sim_tick, start_hour)
        hour = converter.now_to_floor_hour(seconds)
        traveler_number = self.poisson.traveler(hour)
        for traveler in range(traveler_number):
            departure_station = select_random_station(env, sim_tick, start_hour)
            destination_station = select_random_station(env, sim_tick, start_hour, departure_station=departure_station)
            Traveler(departure_station.name, destination_station.name, seconds)
            logging.info("Traveler generated at time %s. Routing from %s to %s" %
                         (converter.seconds_to_string(seconds),
                          departure_station.name,
                          destination_station.name
                          ))
            yield self.env.timeout(int(round(self.ticks_in_second / traveler_number)))


def select_random_station(env, sim_tick, start_hour=0, departure_station=None):
    """
    If departure_station is None, it means that you are looking for
    a random departure_station. Otherwise, it means that you are
    looking for a destination_station.
    """
    is_arrival = departure_station is not None

    second = converter.now_to_seconds(env, sim_tick, start_hour=start_hour)
    city_prob = converter.station_probability(Type.CITY, second, is_arrival=is_arrival)
    neutral_prob = converter.station_probability(Type.NEUTRAL, second, is_arrival=is_arrival)
    residential_prob = converter.station_probability(Type.RESIDENTIAL, second, is_arrival=is_arrival)
    activity_prob = converter.station_probability(Type.ACTIVITY, second, is_arrival=is_arrival)

    prob = random.uniform(0, 1)
    interval = [0, city_prob]

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.CITY, departure_station=departure_station)

    interval[0] = interval[1]
    interval[1] += neutral_prob

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.NEUTRAL, departure_station=departure_station)

    interval[0] = interval[1]
    interval[1] += residential_prob

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.RESIDENTIAL, departure_station=departure_station)

    interval[0] = interval[1]
    interval[1] += activity_prob

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.ACTIVITY, departure_station=departure_station)

    return get_random_station_from_type(Type.CITY, departure_station=departure_station)


def get_random_station_from_type(station_type, departure_station=None):
    """
        If departure_station is None, it means that you are looking for
        a random departure_station. Otherwise, it means that you are
        looking for a destination_station and this station can't be the
        same as the departure_station
    """

    stations = []
    for station in get_stations():
        if station.station_type == station_type.value:
            if departure_station is None:
                stations.append(station)
            elif station.name != departure_station.name:
                stations.append(station)

    if not stations:
        if departure_station is None:
            return random.choice(get_stations())
        else:
            return random.choice(
                [a_station for a_station in get_stations() if a_station.name != departure_station.name])

    return random.choice(stations)
