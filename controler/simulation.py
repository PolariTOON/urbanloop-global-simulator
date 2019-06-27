"""
Classe qui est liée à une simulation
"""
import configparser
import fileinput
import sys
import time
import json
from enum import Enum
import simpy
from math import floor

from controler import probability, converter
from controler.probability import Probability
from controler.routing import Routing
from shutil import copyfile
from settings import simlog


class SimState(Enum):
    RUNNING = 0
    PAUSED = 1
    KILLED = 2


class Simulation:
    def __init__(self, id, is_visualized=False, json_network_path="resources/new_mini_network.json"):
        self.id = id
        # Etape 1 : chargement du modèle
        print("Chargement du modèle : ...")
        with open(json_network_path) as json_data:
            json_network = json.load(json_data)
        self._controler = Routing(self.id, json_network)
        print("Chargement du modèle : [OK]")
        # Etape 2 : chargement de la configuration de la simulation et du modèle probabiliste
        print("Chargement de la configuration : ...")
        self._config = configparser.ConfigParser()
        self._config.read('resources/config.ini')
        print("Chargement de la configuration : [OK]\nChargement du modèle probabiliste : ...")
        self._probability = Probability(self._config['TRAVELER'], self._config['PROB'])
        print("Chargement du modèle probabiliste : [OK]\nInitialisation de simPy : ...")
        # Etape 3 : Initialisation de simPy
        self._env = None
        self._sim_state = SimState.RUNNING
        self._sim_tick = 0.05  # Duration of a tick
        self._current_tick = 0
        self._visualized_tick_duration = 0.05
        self._sim_tick_variations = list()
        self._start_hour = None
        self._endless_quit_event = None
        self._is_real_time = False
        self._is_endless = False
        self._station_refill = True  # Todo : à déplacer dans station
        self._fulfill_period = int(self._config['CAPSULE']['fulfill_period'])
        self._is_visualized = is_visualized
        self._tab_depart = []
        self._tab_temps = []
        self._ascent_generator = None  # ascent_generator.AscentGenerator() # TODO : monter des voyageurs
        if self._config['SIM']['real_time'] in ['true', 'True']:
            self._is_real_time = True
        if self._config['SIM']['endless'] in ['true', 'True']:
            self._is_endless = True
        if self._config['CAPSULE']['station_refill'] in ['false', 'False']:
            self._station_refill = False  # TODO : doit disparaître
        self._load_env()
        self._tick_event = self._env.event()
        self._endless_quit_event = self._env.event()
        # Etape 5 : Lancement de la simulation
        print("Initialisation de simPy : [OK]\nLancement de la simulation : ...")
        self._env.process(self._run_simulation())
        if self._is_endless:
            self._env.run(self._endless_quit_event)
            return
        self._env.run(until=int(self._config['SIM']['duration']))

    def _load_env(self):
        """
        Load the simulation environment with configuration, real_time or not
        """
        if self._is_real_time:
            self._env = simpy.rt.RealtimeEnvironment(factor=self._sim_tick)
        else:
            self._env = simpy.Environment()

    def _modulo_on_seconds(self, seconds):
        """
        This function will return True every simulated seconds. Seconds must be
        greater or equal to 1.
        :param seconds: The desired modulo
        :return: Boolean, if the current_tick is in phase with the given frequency
        """
        if (seconds / self._sim_tick) < 1 or seconds < 1:
            return True
        return self._current_tick % (seconds / self._sim_tick) == 0

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
        print("Simulation is running.")
        tick_start_time = 0
        while True:
            if self._sim_state == SimState.RUNNING:
                print("run")
                loop_sleep_boolean = self._is_visualized and not self._is_real_time and self._visualized_tick_duration != 0
                if loop_sleep_boolean:
                    tick_start_time = time.perf_counter()  # temps de la boucle
                # Etape 1 : génération de statistiques
                # self._controler.travel_stats()  # TODO : génération des statistiques
                # Etape 3 : Passage au tick suivant
                self._env.process(self.tick())
                # Etape 4 : Monter des voyageurs en attente dans les capsules
                self._env.process(
                    self._controler.ascend_travelers(self._config["TRAVELER"]["trip_limit"], self._env))
                # Etape 5 : Génération de nouveaux voyageurs + Etape 6 : Mise à jour du controller
                if self._modulo_on_seconds(1):
                    self._env.process(self.generate_travelers())
                    self._controler.update()  # TODO : Mettre à jour le controler (timers ...)
                # Etape 7 : Complétion des stations
                if self._station_refill and self._current_tick != 0 and self._modulo_on_seconds(1):
                    self._controler.fill_and_full_stations()
                # Etape 8 : gestion des collisions
                #  self.collision() TODO : GESTION DES COLLISIONS
                yield self._env.timeout(1)
                # Etape 9 : Gestion de la fin de la simulation
                if loop_sleep_boolean:
                    sleep_time = self._visualized_tick_duration - (time.perf_counter() - tick_start_time)
                    time.sleep(max(0.0, sleep_time))
            elif self._sim_state == SimState.KILLED:
                print("killed")
                self._controler.extract(self.get_simulated_time())
                self.reset_simulation_parameters("resources/new_mini_network.json")
                if self._is_endless:
                    self._quit_endless_simulation()
                else:
                    yield self._env.process(self._env.exit())
                return

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
            return tick * self._sim_tick

        result = 0
        for start_tick, tick_duration, sim_tick in self._sim_tick_variations:
            if tick <= start_tick + tick_duration:
                return result + (tick - start_tick) * sim_tick
            result += tick_duration * sim_tick

        last_end_tick = self._sim_tick_variations[-1][0] + self._sim_tick_variations[-1][1]
        result += (tick - last_end_tick) * self._sim_tick

        return result

    def reset_simulation_parameters(self, json_network_path):
        """
        Reset the current simulation parameters. The SimState needs to be KILLED
        """
        if self._sim_state != SimState.KILLED:
            return

        simlog.warn("Resetting the simulation parameters")
        with open(json_network_path) as json_data:
            json_network = json.load(json_data)
        self._controler = Routing(self.id, json_network)
        self._current_tick = 0
        self._sim_tick = 0.05
        self._visualized_tick_duration = 0.05
        self._start_hour = None
        self._sim_tick_variations = list()

    def _quit_endless_simulation(self):
        """
        Stop an endless simulation by triggering the _endless_quit_event.
        This function should only be used in SimLoop.loop(), and asserts
        that the simulation is endless
        """

        def _trigger():
            yield self._endless_quit_event.succeed()

        self._env.process(_trigger())

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
            value = self._sim_tick

        if type(self._env) is simpy.rt.RealtimeEnvironment:
            simlog.warn("You can't change the sim_tick in a real-time environment")
            return

        if value <= 0:
            simlog.warn("The sim_tick needs to be greater than zero")
            return

        if self._sim_tick_variations:
            # Not empty case
            start_tick = self._sim_tick_variations[-1][0] + self._sim_tick_variations[-1][1]
            tick_duration = self._current_tick - start_tick
            self._sim_tick_variations.append((start_tick, tick_duration, self._sim_tick))
        else:
            # Empty case
            self._sim_tick_variations.append((0, self._current_tick, self._sim_tick))

        self._sim_tick = value
        simlog.warn("Changing _sim_tick. One tick equals now %f seconds" % self._sim_tick)

    def get_initial_sim_tick(self):
        """
        :return: The _sim_tick value at the start of simulation
        """
        if self._sim_tick_variations:
            return self._sim_tick_variations[0][2]
        return self._sim_tick

    def accelerate_simulation(self):
        initial_sim_tick = self.get_initial_sim_tick()

        if self._visualized_tick_duration > 0:
            self._visualized_tick_duration /= 2
            if self._visualized_tick_duration < initial_sim_tick * 2 ** -8:
                self._visualized_tick_duration = 0
            return

        if self._sim_tick < initial_sim_tick * 2 ** 7:
            self._change_sim_tick(self._sim_tick * 2)

    def decelerate_simulation(self):
        initial_sim_tick = self.get_initial_sim_tick()

        if self._sim_tick > initial_sim_tick:
            self._change_sim_tick(self._sim_tick / 2)
            return

        if self._visualized_tick_duration < initial_sim_tick:
            self._visualized_tick_duration *= 2
            if self._visualized_tick_duration == 0:
                self._visualized_tick_duration = initial_sim_tick * pow(2, -8)

    def change_state(self, sim_state=SimState.RUNNING):
        """
        :param sim_state: The desired simulation state
        """
        simlog.debug("Changing SimState to %s" % sim_state.name)
        self._sim_state = sim_state

    def stop_simulation(self):
        """
        Stop the simulation definitely. After call this method, The SimLoop.loop()
        function will manage the case endless or not, and reset all simulation parameters
        """
        simlog.warn("Simulation KILLED")
        self.change_state(SimState.KILLED)

    def pause_simulation(self):
        """
        Pause the simulation. Call run_simulation_after_pause to restart the simulation
        """
        simlog.warn("Simulation PAUSED")
        self.change_state(SimState.PAUSED)

    def run_simulation_after_pause(self):
        """
        Re-run the simulation after a PAUSED state.
        """
        simlog.warn("Simulation re-RUNNING")
        self.change_state(SimState.RUNNING)

    def get_tick_per_second(self):
        """
        :return: The simulation ticks per second
        """
        return 1 / self._sim_tick

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
        self._controler.ascend_travelers(int(self._config["TRAVELER"]["trip_limit"]), self._env, self._config, self.get_tick_per_second())
