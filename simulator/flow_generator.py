from simulator import poisson
from config import config


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
        hour = hour_from_now(seconds_from_now(env, sim_tick, start_hour))
        traveler_number = self.poisson.generate(hour)
        for traveler in range(traveler_number):
            print("[", env.now, "] Traveler generated at hour :", hour)
            yield self.env.timeout(int(round(self.ticks_in_second / traveler_number)))
