from Simulator import Poisson


def seconds_from_now(env, sim_tick, start_hour=0):
    return env.now * sim_tick + start_hour * 3600


def hour_from_now(now_in_seconds):
    return round((now_in_seconds % 86400) / 3600)


class FlowGenerator:
    def __init__(self, env):
        self.env = env
        self.poisson = Poisson.Poisson()

    def generate_traveler(self, env, sim_tick, start_hour=0):
        while True:
            hour = hour_from_now(seconds_from_now(env, sim_tick, start_hour))
            traveler_number = self.poisson.generate(hour)
            for traveler in range(traveler_number):
                print("Traveler generated at hour : ", hour)
                yield self.env.timeout(int(round(20 / traveler_number)))
