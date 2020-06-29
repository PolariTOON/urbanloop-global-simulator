import sys
from math import floor
from random import random, seed, randint
from simpy import Environment
from model.entities.tokens.traveler import Traveler

from model.entities.nodes.networks.network import Network

from .probability import Probability, generate_traveler_poisson


class Simulation:
    """Simulation du réseau se basant sur simpy"""
    def __init__(self, id, wave, traveler=None, prob=None, running=None, rate=None, max_rate=None, jerky=None, time=None, state=None, **kwargs):
        running = running or False
        rate = rate or 0
        max_rate = max_rate or 7
        jerky = jerky or False
        time = time or 0
        state = state or (seed(), random() * 2 ** 53)[1]
        traveler = traveler or {
            "travelers_per_hour" : 2000,
            "morning_peak_hour" : 8,
            "evening_peak_hour" : 18
        }
        prob = prob or {
            "activity_and_residential_percent" : 30,
            "city_percent" : 20,
            "activity_and_residential_fluctuation" : 20
        }
        self._probability = Probability(prob, traveler)
        self._env = Environment()
        self._wave = wave
        self._running = running
        self._rate = rate
        self._max_rate = max_rate
        self._jerky = jerky
        self._time = time
        self._state = state
        self._network = Network(self._env, id, **kwargs)
        self._env.tick = wave if jerky else wave * 2 ** rate  # Durée d'un tick
        self._env.time = time  # Temps réel actuel en seconde
        self._travelers_per_hour = traveler["travelers_per_hour"]

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, value):
        if value < 0:
            self._rate = 0
        else:
            self._rate = value

    @property
    def max_rate(self):
        return self._max_rate

    @property
    def jerky(self):
        return self._jerky

    @property
    def time(self):
        return self._time

    @property
    def state(self):
        return self._state

    def update(self):
        if not self._running:
            return
        times = 1
        tick = self._wave
        if self._jerky:
            times *= 2 ** self._rate
        else:
            tick *= 2 ** self._rate
        self._env.tick = tick
        for i in range(times):
            self._env.time += self._env.tick
            self._time = self._env.time
            seed(self._state)
            until = floor(self._env.now) + 1
            self._env.run(until=until)
            self._state = random() * 2 ** 53
        second = self._env.time
        if generate_traveler_poisson(self._travelers_per_hour, int(round(second / 3600, 2)), self._env.tick):
            ri = randint(1, len(self._network.stations))
            s = self._network.stations[ri-1]
            r = random()
            if r <= self._probability.station_probability(s.station_type, second, False):
                s._travelers.append(Traveler(self._env, self._env.time))
                s._all_time_count += 1

    def serialize(self):
        dict = self._network.serialize()
        dict.update({
            "running": self.running,
            "rate": self.rate,
            "max_rate": self.max_rate,
            "jerky": self.jerky,
            "time": self.time,
            "state": self.state,
            "modified": True,
        })
        return dict
