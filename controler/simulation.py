import configparser
import fileinput
import sys
import time
from math import floor
from random import random, seed
from simpy import Environment

from controler import probability, converter
from controler.probability import Probability
from controler.routing import Routing
from shutil import copyfile
from settings import simlog


class Simulation:
    """Simulation du réseau se basant sur simpy"""
    def __init__(self, id, state=None, running=None, **kwargs):
        # Etape 1 : chargement de la configuration de la simulation et du modèle probabiliste
        state = state or (seed(), random())[1]
        running = running or False
        self._config = configparser.ConfigParser()
        self._config.read('resources/config.ini')
        self._probability = Probability(self._config['TRAVELER'], self._config['PROB'])
        # Etape 2 : Initialisation de simPy
        self._env = Environment()
        self._state = state
        self._running = running
        # Etape 3 : chargement du modèle
        self._controler = Routing(self._env, id, **kwargs)
        self._env.sim_tick = 0.05  # Duration of a tick
        self._current_tick = 0
        self._visualized_tick_duration = 0.05
        self._sim_tick_variations = []
        self._start_hour = None
        self._station_refill = True  # Todo : à déplacer dans station
        self._fulfill_period = int(self._config['CAPSULE']['fulfill_period'])
        self._tab_depart = []
        self._tab_temps = []
        self._ascent_generator = None  # ascent_generator.AscentGenerator() # TODO : monter des voyageurs
        if self._config['CAPSULE']['station_refill'] in ['false', 'False']:
            self._station_refill = False  # TODO : doit disparaître
        self._tick_event = self._env.event()
        # Etape 5 : Lancement de la simulation
        # self._env.process(self._run_simulation())

    def _modulo_on_seconds(self, seconds):
        """
        This function will return True every simulated seconds. Seconds must be
        greater or equal to 1.
        :param seconds: The desired modulo
        :return: Boolean, if the current_tick is in phase with the given frequency
        """
        if (seconds / self._env._sim_tick) < 1 or seconds < 1:
            return True
        return self._current_tick % (seconds / self._env.sim_tick) == 0

    def tick(self):
        """
        This function triggers the tick_event
        The tick_event updateData the current_tick.
        It should be used to frequency process
        """
        self._current_tick += 1
        yield self._tick_event.succeed()
        self._tick_event = self._env.event()

    def _run_simulation(self):
        """
        This function is the main process station of the simulation.
        You can create several independents process while the
        SimState is RUNNING.
        """
        tick_start_time = 0
        while True:
            if self._running:
                loop_sleep_boolean = self._visualized_tick_duration != 0
                if loop_sleep_boolean:
                    tick_start_time = time.perf_counter()  # temps de la boucle
                # Etape 1 : génération de statistiques
                # self._controler.travel_stats()  # TODO : génération des statistiques
                # Etape 2 : Passage au tick suivant
                self._env.process(self.tick())
                # Etape 3 : Monter des voyageurs en attente dans les capsules
                self._env.process(self.ascend_travelers())
                # Etape 4 : Génération de nouveaux voyageurs + Etape 6 : Mise à jour du controller
                if self._modulo_on_seconds(1):
                    self._env.process(self.generate_travelers())
                    self._controler.update()  # TODO : Mettre à jour le controler (timers ...)
                # Etape 5 : Complétion des stations
                if self._station_refill and self._current_tick != 0 and self._modulo_on_seconds(1):
                    self._controler.fill_and_full_stations()
                # Etape 6 : gestion des collisions
                #  self.collision() TODO : GESTION DES COLLISIONS
                yield self._env.timeout(1)
                # Etape 7 : Gestion de la fin de la simulation
                if loop_sleep_boolean:
                    sleep_time = self._visualized_tick_duration - (time.perf_counter() - tick_start_time)
                    time.sleep(max(0.0, sleep_time))

    def reset_config(self):
        """
        Replace all the values in the config.ini file with default values
        """
        copyfile('resources/default_config.ini', 'resources/config.ini')
        self.restore_config()

    def restore_config(self):
        """
        This function loads the resources/config.ini config file.
        """
        self._config = configparser.ConfigParser()
        self._config.read('resources/config.ini')

    def save_config(self, config_json):
        """
        This function overwrites a new config under a json format and saves it
        into resources/config.ini
        :param config_json: A json with exact same value of attributes
        will be overwritten.
        """
        for line in fileinput.input('resources/config.ini', inplace=True):
            output = line
            for attribute, value in config_json.items():
                if attribute in line and '#' not in line:
                    output = line.split('=')[0].lstrip().rstrip() + '=' + str(value) + '\n'
                    break
            sys.stdout.write(output)
        self.restore_config()

    def serialize_config(self):
        return {
            'travelers_per_day': int(self._config['TRAVELER']['travelers_per_day']),
            'trip_limit': int(self._config['TRAVELER']['trip_limit']),
            'traveler_limit': int(self._config['TRAVELER']['traveler_limit']),
            'ascent_descent_duration': int(self._config['TRAVELER']['ascent_descent_duration']),
            'morning_peak_hour': int(self._config['TRAVELER']['morning_peak_hour']),
            'evening_peak_hour': int(self._config['TRAVELER']['evening_peak_hour']),
            'activity_and_residential_percent': int(self._config['PROB']['activity_and_residential_percent']),
            'city_percent': int(self._config['PROB']['city_percent']),
            'activity_and_residential_fluctuation': int(self._config['PROB']['activity_and_residential_fluctuation']),
            'max_speed': float(self._config['CAPSULE']['max_speed']),
            'number_of_pods': int(self._config['CAPSULE']['number_of_pods']),
            'station_refill': self._config['CAPSULE']['station_refill'],
            'fulfill_period': int(self._config['CAPSULE']['fulfill_period']),
            'switched_cost': int(self._config['ROUTING']['switched_cost']),
            'my_timer': int(self._config['ROUTING']['my_timer']),
            'timer_other': int(self._config['ROUTING']['timer_other']),
            'real_time': self._config['SIM']['real_time'],
            'endless': self._config['SIM']['endless'],
            'duration': int(self._config['SIM']['duration']),
            'start_hour': int(self._config['SIM']['start_hour']),
            'logs': self._config['SIM']['logs']
        }

    def get_simulated_time(self, tick=None):
        """
        :return: The total simulated time, in seconds. This function takes
        into account the sim_tick variation.
        """
        if tick is None or tick > self._current_tick:
            tick = self._current_tick

        if not self._sim_tick_variations:
            # Empty case
            return tick * self._env.sim_tick

        result = 0
        for start_tick, tick_duration, sim_tick in self._sim_tick_variations:
            if tick <= start_tick + tick_duration:
                return result + (tick - start_tick) * sim_tick
            result += tick_duration * sim_tick

        last_end_tick = self._sim_tick_variations[-1][0] + self._sim_tick_variations[-1][1]
        result += (tick - last_end_tick) * self._env.sim_tick

        return result

    def _change_sim_tick(self, value=None):
        """
        Change the current sim_tick value. Bigger is the sim_tick value,
        more jerky the simulation will be. Use this to speed up (really)
        the simulation. This function adds in the variations list, the tuple :
        (start_tick, tick_duration, sim_tick) in _sim_tick_variations
        /!\ This function is disabled in case of real time simulation
        :param value: The desired new sim_tick value
        """
        if value is None:
            value = self._env.sim_tick

        if value <= 0:
            simlog.warn("The sim_tick needs to be greater than zero")
            return

        if self._sim_tick_variations:
            # Not empty case
            start_tick = self._sim_tick_variations[-1][0] + self._sim_tick_variations[-1][1]
            tick_duration = self._current_tick - start_tick
            self._sim_tick_variations.append((start_tick, tick_duration, self._env.sim_tick))
        else:
            # Empty case
            self._sim_tick_variations.append((0, self._current_tick, self._env.sim_tick))

        self._env.sim_tick = value
        simlog.warn("Changing _sim_tick. One tick equals now %f seconds" % self._env.sim_tick)

    def get_initial_sim_tick(self):
        """
        :return: The _sim_tick value at the start of simulation
        """
        if self._sim_tick_variations:
            return self._sim_tick_variations[0][2]
        return self._env.sim_tick

    def accelerate_simulation(self):
        """
        Accélère la simulation par 2, 8 palliers où l'on modifie le temps visualisé, après cela on
        passe à une modification de la durée d'un tick
        :return: (void)
        """
        initial_sim_tick = self.get_initial_sim_tick()

        if self._visualized_tick_duration > 0:
            self._visualized_tick_duration /= 2
            if self._visualized_tick_duration < initial_sim_tick * 2 ** -8:
                self._visualized_tick_duration = 0
            return

        if self._env.sim_tick < initial_sim_tick * 2 ** 7:
            self._change_sim_tick(self._env.sim_tick * 2)

    def decelerate_simulation(self):
        """
        Rend la simulation deux fois plus lente, avec les mêmes intervalles que pour l'accélération
        :return: (void)
        """
        initial_sim_tick = self.get_initial_sim_tick()

        if self._env.sim_tick > initial_sim_tick:
            self._change_sim_tick(self._env.sim_tick / 2)
            return

        if self._visualized_tick_duration < initial_sim_tick:
            self._visualized_tick_duration *= 2
            if self._visualized_tick_duration == 0:
                self._visualized_tick_duration = initial_sim_tick * pow(2, -8)

    def get_tick_per_second(self):
        """
        :return: The simulation ticks per second
        """
        return 1 / self._env.sim_tick

    def generate_travelers(self):
        """
        :return: The generator of one or several travelers each second
        """
        traveler_limit = int(self._config["TRAVELER"]["traveler_limit"])
        seconds = self.now_to_seconds()
        hour = converter.seconds_to_floor_hour(seconds)
        traveler_number = probability.generate_traveler_poisson(self._config["TRAVELER"]["travelers_per_day"], hour)
        self._controler.generate_travelers(traveler_limit, traveler_number, seconds, self._probability)
        yield self._env.timeout(floor(self.get_tick_per_second() / traveler_number))

    def now_to_seconds(self):
        """
        :return: The current time in second. This function takes into account the
        sim_tick variations.
        """
        if self._start_hour is None:
            return -1
        return self._start_hour * 3600 + self.get_simulated_time()

    def ascend_travelers(self):
        yield self._env.process(self._controler.ascend_travelers(self._env, self.now_to_seconds(), self._probability, self._config, self.get_tick_per_second()))

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value):
        self._running = value

    def update(self):
        if self._running:
            seed(self._state)
            until = floor(self._env.now) + 1
            self._env.run(until=until)
            self._state = random()

    def serialize(self):
        dict = self._controler._network.serialize()
        state = self._state
        running = self._running
        dict.update({
            "state": state,
            "running": running
        })
        return dict
