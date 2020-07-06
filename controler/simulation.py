import sys
from math import floor
from random import random, seed, randint
from simpy import Environment
from model.entities.tokens.traveler import Traveler
from model.entities.nodes.networks.network import Network
from random import choice
from .probability import Probability, generate_traveler_poisson


class Simulation:
    """Simulation du réseau se basant sur simpy"""
    def __init__(self, id, wave, traveler=None, prob=None, running=None, rate=None, max_rate=None, jerky=None, time=None, state=None, **kwargs):
        """
        "id" (entier positif) id du réseau
        "wave" (flottant positif) pas de simulation
        "traveler" paramètres de génération des voyageurs
        "prob" paramètres d'appartion des voyageurs
        "running" (booléen) un booléen indiquant si la simulation est déjà lancée (car on peut faire une sauvegarde d’un réseau en cours de simulation)
        "rate" (entier positif) le logarithme en base 2 de la vitesse de la simulation
        "max_rate" (entier positif) le logarithme en base 2 de la vitesse maximale de la simulation
        "jerky" (booléen) un booléen indiquant l’algorithme utilisé pour accélérer la simulation
        "time" (flottant positif) le temps simulé de reprise de la simulation (en s)
        "state" (flottant) un seed permettant de choisir le générateur pseudo-aléatoire utilisé et donc de relancer une même simulation dans les mêmes conditions
        """
        running = running or False
        rate = rate or 0
        max_rate = max_rate or 7
        jerky = jerky or False
        time = time or 0
        state = state or (seed(), random() * 2 ** 53)[1]
        traveler = traveler or {
            "travelers_per_hour": 2000,
            "morning_peak_hour": 8,
            "evening_peak_hour": 18
        }
        prob = prob or {
            "activity_and_residential_percent": 30,
            "city_percent": 20,
            "activity_and_residential_fluctuation": 20
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
        if not self._running:   # simulation en pause
            return
        times = 1
        tick = self._wave
        if self._jerky:  # mode jerky
            times *= 2 ** self._rate
        else:  # mode standard
            tick *= 2 ** self._rate
        self._env.tick = tick
        for i in range(times):  # dans le mode jerky, on calcule plusieurs ticks à la fois
            self._env.time += self._env.tick  # on incrémente le temps
            self._time = self._env.time
            seed(self._state)  # à appeler avant d'utiliser random
            until = floor(self._env.now) + 1  # durée de simulation calculée
            self._env.run(until=until)
            self._state = random() * 2 ** 53
        second = self._env.time

        if generate_traveler_poisson(self._travelers_per_hour, int(round(second / 3600, 2)), self._env.tick):
            ri = randint(1, len(self._network.stations))
            s = self._network.stations[ri-1]
            r = random()
            if r <= self._probability.station_probability(s.station_type, second, False):  # si le nombre aléatoire généré est inférieur à la probabilité d'appartion
                # la source est là où le traveler est généré
                # la destination une des autres stations
                traveler_source = s.name
                stations = self._network.stations_names.copy()
                stations.remove(s.name)
                traveler_destination = choice(stations)
                s.travelers.append(Traveler(self._env, self._env.time, source=traveler_source, destination=traveler_destination))  # alors un voyageur est généré
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
