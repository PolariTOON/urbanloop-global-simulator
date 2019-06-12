"""
Classe qui est liée à une simulation
"""
import configparser
import fileinput
import os
import sys
import time
from enum import Enum

import simpy

from controler.probability import Probability
from controler.routing import Routing
from shutil import copyfile

from stats import stats_recorder


class SimState(Enum):
    RUNNING = 0
    PAUSED = 1
    KILLED = 2


class Simulation:
    def __init__(self, loaded=None, modified=None, config=None, is_visualized=False):
        self.controler = Routing()
        self.loaded = loaded
        self.config = config
        self.modified = modified
        self.traveler = config['TRAVELER']
        self.topology = config['TOPOLOGY']
        self.prob = config['PROB']
        self.capsule = config['CAPSULE']
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
        self.recorder = stats_recorder.StatsRecorder(0)
        self.is_real_time = False
        self.is_endless = False
        self.station_refill = True
        self.fulfill_period = int(self.capsule['fulfill_period'])
        self.is_visualized = is_visualized
        self.tab_depart = []
        self.tab_temps = []
        self.traveler_generator = None  # traveler_generator.TravelerGenerator() # TODO : generation de voyageur
        self.ascent_generator = None  # ascent_generator.AscentGenerator() # TODO : monter des voyageurs
        if self.sim['real_time'] in ['true', 'True']:
            self.is_real_time = True
        if self.sim['endless'] in ['true', 'True']:
            self.is_endless = True
        if self.capsule['station_refill'] in ['false', 'False']:
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
                    """
                    On obtient dans staats le temps moyen de trajet des capsules et dans staatsvoy le temps moyen
                    d'attentes des voyageurs
                    """
                    latest_stats_file = open("out/staats.txt", "a+")
                    buffer = str(self.controler.temps_moy()) + ","  # TODO : stats temps moyen
                    latest_stats_file.write(buffer)
                    latest_stats_file.close()
                    latest_stats_file = open("out/staatsvoy.txt", "a+")
                    buffer = str(self.controler.temps_moy_voy()) + ","  # TODO : stats temps moyen
                    latest_stats_file.write(buffer)
                    latest_stats_file.close()

                # Information about the network : TODO
                if self._modulo_on_seconds(30):
                    loops = []
                    capsules = {}
                    for a_loop_name, a_loop in loop.all_loops.items():
                        loops.append(a_loop)
                        capsules[a_loop_name] = 0
                    for a_capsule in capsule.get_capsules():
                        capsules[a_capsule.loop.name] += 1
                    for a_loop in loops:
                        recorder.add_capsule_average_loop(capsules[a_loop.name], a_loop)
                    for a_station in station.get_stations():
                        recorder.add_stopped_capsules_station(a_station.get_waiting_capsules_number(), a_station)
                        recorder.add_waiting_travelers(a_station.get_waiting_travelers_number(), a_station)

                _env.process(self.tick())
                _env.process(self.ascent_generator.generate())
                if _modulo_on_seconds(1):
                    _env.process(self.traveler_generator.generate())
                    self.controller.update()

                if self.station_refill and not _current_tick == 0 and _modulo_on_seconds(1):
                    station.fill_and_full_stations()

                self.collision()

                yield _env.timeout(1)

                if loop_sleep_boolean:
                    sleep_time = _visualized_tick_duration - (time.perf_counter() - tick_start_time)
                    time.sleep(max(0.0, sleep_time))
            elif is_killed():
                recorder.stop_listen(get_simulated_time())
                recorder.extract()
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
        self.capsule = self.config['CAPSULE']
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
            'max_speed': float(self.capsule['max_speed']),
            'number_of_capsules': int(self.capsule['number_of_capsules']),
            'station_refill': self.capsule['station_refill'],
            'fulfill_period': int(self.capsule['fulfill_period']),
            'switched_cost': int(self.routing['switched_cost']),
            'my_timer': int(self.routing['my_timer']),
            'timer_other': int(self.routing['timer_other']),
            'real_time': self.sim['real_time'],
            'endless': self.sim['endless'],
            'duration': int(self.sim['duration']),
            'start_hour': int(self.sim['start_hour']),
            'logs': self.sim['logs']
        }
