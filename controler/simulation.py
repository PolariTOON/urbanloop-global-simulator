from configparser import ConfigParser
from math import floor
from random import random, seed
from simpy import Environment

from model.entities.nodes.networks.network import Network

from .probability import Probability


class Simulation:
    """Simulation du réseau se basant sur simpy"""
    def __init__(self, id, sim_tick, time=None, state=None, running=None, **kwargs):
        state = state or (seed(), random() * 2 ** 53)[1]
        running = running or False
        self._config = ConfigParser()
        self._config.read('resources/config.ini')  # TODO : déplacer ce qui est nécessaire dans le json
        self._probability = Probability(self._config['TRAVELER'], self._config['PROB'])
        self._env = Environment()
        self._time = time
        self._state = state
        self._running = running
        self._network = Network(self._env, id, **kwargs)
        self._env.sim_tick = sim_tick  # Durée d'un tick
        self._env.time = time  # Temps réel actuel en seconde

    @property
    def time(self):
        return self._time

    @property
    def state(self):
        return self._state

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def update(self):
        if self._running:
            self._env.time += self._env.sim_tick
            self._time = self._env.time
            seed(self._state)
            until = floor(self._env.now) + 1
            self._env.run(until=until)
            self._state = random() * 2 ** 53

    def serialize(self):
        dict = self._network.serialize()
        dict.update({
            "time": self.time,
            "state": self.state,
            "running": self.running
        })
        return dict
