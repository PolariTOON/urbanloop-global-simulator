"""
C'est ici qu'est le controler du paradigme SDN (calcul des routes ...)
"""
import random

from math import inf

from model.networks.network import Network
from settings import simlog
from stats.stats_recorder import StatsRecorder


class Routing:
    def __init__(self, id, json_network):
        self._id = id
        self._network = Network(self._id, **json_network)
        self._recorder = StatsRecorder(0)  # TODO : à déplacer ici
        self._timers = [-1] * len(self._network.pods)
        self._tab_depart = []
        self._tab_temps = []
        self._tab_depart_voy = []
        self._tab_temps_voy = []
        self.matrix = [[inf for j in range(len(self._network.switches))] for i in range(len(self._network.switches))]
        self.expected_matrix = [[inf for j in range(len(self._network.switches))] for i in range(len(self._network.switches))]
        """
        # Init de la matrice au sein des boucles boucle
        for current_switch in self._network.switches:
            self.matrix[switch.id][switch.next.next.id] = 
        """

    def travel_stats(self):
        """
        On obtient dans staats le temps moyen de trajet des capsules et dans staatsvoy le temps moyen
        d'attentes des voyageurs
        """
        latest_stats_file = open("out/staats.txt", "a+")
        buffer = str(self.temps_moy()) + ","
        latest_stats_file.write(buffer)
        latest_stats_file.close()
        latest_stats_file = open("out/staatsvoy.txt", "a+")
        buffer = str(self.temps_moy_voy()) + ","
        latest_stats_file.write(buffer)
        latest_stats_file.close()

    def temps_moy_stat(self, id, temps):
        test = True
        for i in self._tab_depart:
            if i[0] == id:
                test = False
                self._tab_temps.append(temps - i[1])
                i[0] = -1
        if test:
            self._tab_depart.append([id, temps])

    def temps_moy_voy_stat(self, id, temps):
        test = True
        for i in self._tab_depart_voy:
            if i[0] == id:
                test = False
                self._tab_temps_voy.append(temps - i[1])
                i[0] = -1
        if test:
            self._tab_depart_voy.append([id, temps])

    def temps_moy_voy(self):
        moy = 0
        j = 0
        for i in self._tab_temps_voy:
            j += 1
            moy += i
        if j == 0:
            return 0
        else:
            return moy / j

    def temps_moy(self):
        moy = 0
        j = 0
        for i in self._tab_temps:
            j += 1
            moy += i
        if j == 0:
            return 0
        else:
            return moy / j

    def extract(self, simulated_time):
        self._recorder.stop_listen(simulated_time)
        self._recorder.extract()

    def update(self):
        pass

    def ascend_travelers(self, trip_limit, _env, config, frequency):
        for station in self._network.stations:
            if station.travelers and station.pods and (trip_limit > 0 or trip_limit == -1):
                if trip_limit != -1:
                    trip_limit -= 1
                if station.pods:
                    return

                traveler = station.travelers.pop()
                pod = station.pods[-1]
                pod.add_traveler(traveler)
                # sim_loop.recorder.add_waiting_time_traveler(traveler.get_waiting_seconds(), traveler) TODO : STATS A GENERER
                yield _env.process(ascent_event(station, pod, _env, config["TRAVELER"]["ascent_descent_duration"], frequency))

    def generate_travelers(self, traveler_limit, traveler_number, second, probability):
        for a_traveler in range(traveler_number):
            if not (traveler_limit > 0 or traveler_limit == -1):
                return
            if traveler_limit != -1:
                traveler_limit -= 1

            source = self._network.select_random_station(second, probability)
            destination = self._network.select_random_station(second, probability, departure_station=source)
            source.add_traveler(destination)
            # self.temps_moy_voy_stat(self.id, sim_loop.get_simulated_time())  # TODO : STATS A GERER
            simlog.info("Traveler generated", source, destination)


def ascent_event(station, pod, _env, ascent_descent_duration, frequency):
    ascent_timeout = _env.timeout(random_ascent_descent_duration(ascent_descent_duration, frequency))
    ascent_timeout.callbacks.append(lambda event: ascent_event_callback(station, pod))
    yield ascent_timeout


def random_ascent_descent_duration(ascent_descent_duration, frequency):
    """
    :return: A value between [|time-2, time+2|]. time is the defined duration (in the config file)
    for ascent and descent events.
    """
    random_seconds = random.randrange(ascent_descent_duration - 2, ascent_descent_duration + 2, 1)
    return random_seconds * frequency


def ascent_event_callback(station, pod):
    station.pods.remove(pod)
    pod.start_trip()  # TODO : à faire
