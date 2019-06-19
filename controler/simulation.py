"""
Classe qui est liée à une simulation
"""
import configparser
import fileinput
import os
import sys
import time
import json
from enum import Enum

import simpy

from controler.probability import Probability
from controler.routing import Routing
from shutil import copyfile


class SimState(Enum):
    RUNNING = 0
    PAUSED = 1
    KILLED = 2


class Simulation:
    def __init__(self, loaded=None, modified=None, config=None, is_visualized=False, json_network_path="resources/new_mini_network.json"):
        with open(json_network_path) as json_data:
            json_network = json.load(json_data)
        self.controler = Routing(json_network)
        self.loaded = loaded
        self.config = config
        self.modified = modified
        self.traveler = config['TRAVELER']
        self.topology = config['TOPOLOGY']
        self.prob = config['PROB']
        self.pod = config['POD']
        self.routing = config['ROUTING']
        self.sim = config['SIM']
        self.path = 'resources/config.ini'
        self.default_path = 'resources/default_config.ini'
        self.probability = Probability(self.traveler, self.prob)
        self._env = None
        self._sim_state = None
        self._sim_tick = 0.05  # Duration of a tick
        self._current_tick = 0
        self._visualized_tick_duration = 0.05
        self._sim_tick_variations = list()
        self._start_hour = None
        self._endless_quit_event = None
        self.is_real_time = False
        self.is_endless = False
        self.station_refill = True
        self.fulfill_period = int(self.pod['fulfill_period'])
        self.is_visualized = is_visualized
        self.tab_depart = []
        self.tab_temps = []
        self.traveler_generator = None  # traveler_generator.TravelerGenerator() # TODO : generation de voyageur
        self.ascent_generator = None  # ascent_generator.AscentGenerator() # TODO : monter des voyageurs
        if self.sim['real_time'] in ['true', 'True']:
            self.is_real_time = True
        if self.sim['endless'] in ['true', 'True']:
            self.is_endless = True
        if self.pod['station_refill'] in ['false', 'False']:
            self.station_refill = False
        self._load_env()
        self.tick_event = self._env.event()
        self._endless_quit_event = self._env.event()
        self._env.process(self.loop())

    def _load_env(self):
        """
        Load the simulation environment with configuration, real_time or not
        """
        if self.is_real_time:
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
        yield self.tick_event.succeed()
        self.tick_event = self._env.event()

    def loop(self):
        """
        This function is the main process station of the simulation.
        You can create several independents process while the
        SimState is RUNNING.
        """
        tick_start_time = 0
        while True:
            if self.is_running():
                loop_sleep_boolean = self.is_visualized and not self.is_real_time and self._visualized_tick_duration != 0
                if loop_sleep_boolean:
                    tick_start_time = time.perf_counter()  # temps de la boucle

                # Stats are recorded every 30 simulated seconds
                if self._modulo_on_seconds(30):
                    try:
                        os.mkdir("out")
                    except:
                        pass
                    self.controler.travel_stats()


                # Information about the network : TODO : Gestion des infos du circuit à faire depuis le controler (routing)
                if self._modulo_on_seconds(30):
                    self.controler.maj_info()

                self._env.process(self.tick())
                self._env.process(self.ascent_generator.generate())  # TODO : générer la montée des voyageurs à chaque tick
                if self._modulo_on_seconds(1):
                    self._env.process(self.traveler_generator.generate())  # TODO : générer les voyageurs à chaque tick
                    self.controller.update()  # TODO : Mettre à jour le controler (timers ...)

                if self.station_refill and not self._current_tick == 0 and self._modulo_on_seconds(1):
                    self.controler.fill_and_full_stations()

                self.collision()

                yield self._env.timeout(1)

                if loop_sleep_boolean:
                    sleep_time = self._visualized_tick_duration - (time.perf_counter() - tick_start_time)
                    time.sleep(max(0.0, sleep_time))
            elif self.is_killed():
                self.controler.extract(self.get_simulated_time())
                reset_simulation_parameters()
                if self.is_endless:
                    _quit_endless_simulation()
                else:
                    yield _env.process(_env.exit())
                return

    def is_running(self):
        """
        :return: True if the simulation is currently started
        """
        return self._sim_state == SimState.RUNNING

    def is_killed(self):
        """
        :return: True if the simulation is currently paused
        """
        return self._sim_state == SimState.KILLED

    def reset_config(self):
        """
        Replace all the values in the config.ini file with default values
        """
        copyfile(self.default_path, self.path)
        self.restore_config()

    def restore_config(self):
        """
        This function loads the resources/config.ini config file.
        """
        self.config = configparser.ConfigParser()
        self.config.read(self.path)
        self.traveler = self.config['TRAVELER']
        self.topology = self.config['TOPOLOGY']
        self.prob = self.config['PROB']
        self.pod = self.config['POD']
        self.routing = self.config['ROUTING']
        self.sim = self.config['SIM']
        self.loaded = True

    def save_config(self, config_json):
        """
        This function overwrites a new config under a json format and saves it
        into resources/config.ini
        :param config_json: A json with exact same value of attributes
        will be overwritten.
        """
        for line in fileinput.input(self.path, inplace=True):
            output = line
            for attribute, value in config_json.items():
                if attribute in line and '#' not in line:
                    output = line.split('=')[0].lstrip().rstrip() + '=' + str(value) + '\n'
                    break
            sys.stdout.write(output)
        self.restore_config()

    def serialize_config(self):
        if self.loaded is False:
            return None
        return {
            'travelers_per_day': int(self.traveler['travelers_per_day']),
            'trip_limit': int(self.traveler['trip_limit']),
            'traveler_limit': int(self.traveler['traveler_limit']),
            'ascent_descent_duration': int(self.traveler['ascent_descent_duration']),
            'morning_peak_hour': int(self.traveler['morning_peak_hour']),
            'evening_peak_hour': int(self.traveler['evening_peak_hour']),
            'network_file': self.topology['network_file'],
            'activity_and_residential_percent': int(self.prob['activity_and_residential_percent']),
            'city_percent': int(self.prob['city_percent']),
            'activity_and_residential_fluctuation': int(self.prob['activity_and_residential_fluctuation']),
            'max_speed': float(self.pod['max_speed']),
            'number_of_pods': int(self.pod['number_of_pods']),
            'station_refill': self.pod['station_refill'],
            'fulfill_period': int(self.pod['fulfill_period']),
            'switched_cost': int(self.routing['switched_cost']),
            'my_timer': int(self.routing['my_timer']),
            'timer_other': int(self.routing['timer_other']),
            'real_time': self.sim['real_time'],
            'endless': self.sim['endless'],
            'duration': int(self.sim['duration']),
            'start_hour': int(self.sim['start_hour']),
            'logs': self.sim['logs']
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
