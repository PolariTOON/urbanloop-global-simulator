from simulator import poisson
from settings import config
from simulator import converter
import logging


def seconds_from_now(env, sim_tick, start_hour=0):
    return env.now * sim_tick + start_hour * 3600


def hour_from_now(now_in_seconds):
    return round((now_in_seconds % 86400) / 3600)


class FlowGenerator:
    def __init__(self, env):
        self.env = env
        self.poisson = poisson.Poisson()
        self.ticks_in_second = 1 / float(config.sim['tick'])

    def generate_traveler(self, env, sim_tick, start_hour=0):
        seconds = seconds_from_now(env, sim_tick, start_hour)
        hour = hour_from_now(seconds)
        traveler_number = self.poisson.traveler(hour)
        for traveler in range(traveler_number):
            logging.info("Traveler generated at time %s" % converter.convert_seconds(seconds))
            yield self.env.timeout(int(round(self.ticks_in_second / traveler_number)))

