"""
C'est ici qu'est le controler du paradigme SDN (calcul des routes ...)
"""
from model.networks.network import Network
from stats import stats_recorder


class Routing:
    def __init__(self, json_network):
        self.network = Network(json_network)
        self.recorder = stats_recorder.StatsRecorder(0)
        self.timers = [-1] * len(self.network.get_capsules())
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

    def maj_info(self):
        loops = []
        pods = []
        for a_loop_name, a_loop in self.network.get_loops():
            loops.append(a_loop)
            pods[a_loop_name] = 0
        for a_pod in self.network.get_pods():
            pods[a_pod.loop.name] += 1
        for a_loop in loops:
            recorder.add_pod_average_loop(pods[a_loop.name], a_loop)
        for a_station in station.get_stations():
            recorder.add_stopped_pods_station(a_station.get_waiting_pods_number(), a_station)
            recorder.add_waiting_travelers(a_station.get_waiting_travelers_number(), a_station)

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
