import configparser
from math import floor
from random import random, seed
from simpy import Environment

from model.entities.nodes.networks.network import Network

from .probability import Probability


# TODO : monter des voyageurs

class Simulation:
    """Simulation du réseau se basant sur simpy"""
    def __init__(self, id, sim_tick, time=None, state=None, running=None, **kwargs):
        # Etape 1 : chargement de la configuration de la simulation et du modèle probabiliste
        state = state or (seed(), random() * 2 ** 53)[1]
        running = running or False
        self._config = configparser.ConfigParser()
        self._config.read('resources/config.ini')
        self._probability = Probability(self._config['TRAVELER'], self._config['PROB'])  # TODO: déplacer vers le fichier JSON d'un réseau
        # Etape 2 : Initialisation de simPy
        self._env = Environment()
        self._time = time
        self._state = state
        self._running = running
        # Etape 3 : chargement du modèle
        self._network = Network(self._env, id, **kwargs)
        self._env.sim_tick = sim_tick  # Duration of a tick todo tristan : en lien avec les vitesses des capsules
        self._env.time = time
        self._fulfill_period = int(self._config['CAPSULE']['fulfill_period'])

    def _modulo_on_seconds(self, seconds):
        """
        This function will return True every simulated seconds. Seconds must be
        greater or equal to 1.
        :param seconds: The desired modulo
        :return: Boolean, if the current_tick is in phase with the given frequency
        """
        if (seconds / self._env.sim_tick) < 1 or seconds < 1:
            return True
        return int(self._env.now) % (seconds / self._env.sim_tick) == 0

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
            self._env.time += self._env.sim_tick  # TODO: à calculer
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
