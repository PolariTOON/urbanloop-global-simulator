"""
C'est ici qu'est le controler du paradigme SDN (calcul des routes ...)
"""
from model.networks.network import Network
from model.networks.tokens.traveler import Traveler
from settings import simlog
from stats.stats_recorder import StatsRecorder


class Routing:
    def __init__(self, id, json_network):
        self.id = id
        self.network = Network(self.id, **json_network)
        self.recorder = StatsRecorder(0)  # TODO : à déplacer ici
        self.timers = [-1] * len(self.network.pods)
        self.tab_depart = []
        self.tab_temps = []
        self.tab_depart_voy = []
        self.tab_temps_voy = []

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
        for i in self.tab_depart:
            if i[0] == id:
                test = False
                self.tab_temps.append(temps - i[1])
                i[0] = -1
        if test:
            self.tab_depart.append([id, temps])

    def temps_moy_voy_stat(self, id, temps):
        test = True
        for i in self.tab_depart_voy:
            if i[0] == id:
                test = False
                self.tab_temps_voy.append(temps - i[1])
                i[0] = -1
        if test:
            self.tab_depart_voy.append([id, temps])

    def temps_moy_voy(self):
        moy = 0
        j = 0
        for i in self.tab_temps_voy:
            j += 1
            moy += i
        if j == 0:
            return 0
        else:
            return moy / j

    def temps_moy(self):
        moy = 0
        j = 0
        for i in self.tab_temps:
            j += 1
            moy += i
        if j == 0:
            return 0
        else:
            return moy / j

    def extract(self, simulated_time):
        self.recorder.stop_listen(simulated_time)
        self.recorder.extract()

    def update(self):
        pass

    def ascend_travelers(self, trip_limit, _env):
        for station in self.network.stations:
            if station.travelers and station.pods and self.can_generate():
                if trip_limit != -1:
                    trip_limit -= 1
                if station.pods:
                    return

                traveler = station.travelers.pop()
                pod = station.pods[-1]
                pod.add_traveler(traveler)
                # sim_loop.recorder.add_waiting_time_traveler(traveler.get_waiting_seconds(), traveler) TODO : STATS A GENERER
                yield _env.process(ascent_event(station, pod, _env))

    def generate_travelers(self, traveler_limit, traveler_number, second, probability):
        for a_traveler in range(traveler_number):
            if not (traveler_limit > 0 or traveler_limit == -1):
                return
            if traveler_limit != -1:
                traveler_limit -= 1

            departure_station = self.network.select_random_station(second, probability)
            destination_station = self.network.select_random_station(second, probability,
                                                                     departure_station=departure_station)
            a = Traveler(departure_station, destination_station)  # TODO : A GERER
            self.temps_moy_voy_stat(self.id, sim_loop.get_simulated_time())  # TODO : A GERER
            simlog.info("Traveler generated", departure_station, destination_station)


def ascent_event(a_station, capsule, _env):  # TODO à ajuster
    ascent_timeout = _env.timeout(converter.random_ascent_descent_duration())
    ascent_timeout.callbacks.append(lambda event: ascent_event_callback(a_station, capsule))
    yield ascent_timeout


def ascent_event_callback(a_station, capsule):  # TODO : à ajuster
    a_station.capsule_queue.remove(capsule)
    capsule.start_trip()
