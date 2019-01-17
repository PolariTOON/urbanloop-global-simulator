import logging
import random

from model.station import *
from model.capsule import *
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
            departure_station = select_random_station(env, sim_tick, start_hour, is_arrival=True)
            destination_station = select_random_station(env, sim_tick, start_hour, is_arrival=False)
            capsule = Capsule(None, departure_station)
            capsule.final_destination = destination_station
            logging.info("Traveler generated at time %s. Routing from %s to %s" %
                         (converter.seconds_to_string(seconds),
                          departure_station.name,
                          destination_station.name
                          ))
            yield self.env.timeout(int(round(self.ticks_in_second / traveler_number)))


def select_random_station(env, sim_tick, start_hour=0, is_arrival=True):
    second = converter.now_to_seconds(env, sim_tick, start_hour=start_hour)
    city_prob = converter.station_probability(Type.CITY, second, is_arrival=is_arrival)
    neutral_prob = converter.station_probability(Type.NEUTRAL, second, is_arrival=is_arrival)
    residential_prob = converter.station_probability(Type.RESIDENTIAL, second, is_arrival=is_arrival)
    activity_prob = converter.station_probability(Type.ACTIVITY, second, is_arrival=is_arrival)

    prob = random.uniform(0, 1)
    interval = [0, city_prob]

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.CITY)

    interval += [interval[1], neutral_prob]

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.NEUTRAL)

    interval += [interval[1], residential_prob]

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.RESIDENTIAL)

    interval += [interval[1], activity_prob]

    if interval[0] <= prob < interval[1]:
        return get_random_station_from_type(Type.ACTIVITY)

    return get_random_station_from_type(Type.CITY)


def get_random_station_from_type(station_type):
    stations = [station for station in get_stations() if station.station_type == station_type]
    return random.choice(stations)
