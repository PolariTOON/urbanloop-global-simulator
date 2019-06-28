"""
C'est ici qu'est le controler du paradigme SDN (calcul des routes ...)
"""
import random
from cmath import inf

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
        for route in self._network.routes:
            weight = 0
            for section in route.sections:
                weight += section.weight
            route.weight = weight

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

    def update(self):  # TODO
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
                yield _env.process(
                    ascent_event(station, pod, _env, config["TRAVELER"]["ascent_descent_duration"], frequency))

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

    def calcul(self, switch_start, switch_destination):  # TODO : A FAIRE
        """
        calcul du chemin optimal entre deux aiguillages
        Il s'agit d'un Dijkstra.
        :param switch_start: destination OBLIGATOIRE
        :param  switch_destination : depart OBLIGATOIRE
        :return: path : le chemin optimal : liste ordonnée (sens croissant) des routes traversées pour aller
        d'un aiguillage à l'autre
        """
        VISITED = inf
        distance = len(self._network.switches) * [VISITED]
        distance[switch_start.id] = 0

        visited_routes = [-1] * len(self._network.switches)

        predecessors = len(self._network.switches) * [None]

        def maj_distances(switch1, switch2):
            if switch1.next.next == switch2:
                weight = switch1.next.weight
            elif switch1.beside.next == switch2:
                weight = switch1.beside.weight
            else:
                return
            if distance[switch2.id] > distance[switch1.id] + weight:
                distance[switch2.id] = distance[switch1.id] + weight
                predecessors[switch2.id] = switch1
                for i in range(len(visited_routes)):
                    if visited_routes[i] == switch2.id:
                        visited_routes[i] = -1

        def f(current_switch, previous_switch):
            # Initialisation
            if previous_switch is None:
                visited_routes[current_switch.id] = VISITED

                for n in node.next_nodes:
                    if n is not None:
                        maj_distances(node, n)

                for n in node.next_nodes:
                    if n is not None:
                        f(n, node)

            elif visited_nodes[node.id] < VISITED and visited_nodes[node.id] != pred_Node.id:
                if visited_nodes[node.id] == -1:
                    visited_nodes[node.id] = pred_Node.id
                elif visited_nodes[node.id] < VISITED:
                    visited_nodes[node.id] = VISITED

                for n in node.next_nodes:
                    if n is not None:
                        maj_distances(node, n)

                for n in node.next_nodes:
                    if n is not None:
                        f(n, node)

        f(node_start, None)
        path = list()
        current_node = node_arrival
        while predecessor[current_node.id] is None:
            current_node = current_node.previous_nodes[0]
        while current_node.id != node_start.id:
            path.append(current_node)
            current_node = predecessor[current_node.id]

        path.append(node_start)
        return path


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


def update_weight(switch1, switch2, travel_time):
    """
    Met à jour le poids de la route reliant switch1 à switch2 q'une capsule vient de parcourir
    S'ils ne sont pas reliés alors ne fait rien
    :param travel_time: temps mis par la capsule pour parcourir la route
    :param switch1: switch précédent la route empruntée par la capsule
    :param switch2: switch suivant la route empruntée par la capsule
    :return: boolean indiquant si il y a congestion
    """
    if switch1.next.next == switch2:
        route = switch1.next
    elif switch1.beside.next == switch2:
        route = switch1.beside
    else:
        return False
    route.weight = 0.875 * route.weight + 0.125 * travel_time
    return route.weight > 3 * route.expected_weight


def no_more_congestion(previous_switch, current_switch):
    """
    :param previous_switch: aiguillage précédent
    :param current_switch: aiguillage actuel
    :return: boolean étant true s'il n'y a plus de congestion sur la route entre les deux aiguillages et false sinon
    """
    if previous_switch.next.next == current_switch:
        route = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        route = previous_switch.beside
    else:
        return True
    return route.weight < 2 * route.expected_weight


def disable_route(previous_switch, current_switch):
    """
    Rend impossible le passage par une route, ie met le poids de celle-ci à l'infini
    :param previous_switch: aiguillage de début de route
    :param current_switch: aiguillage de fin de route
    """
    if previous_switch.next.next == current_switch:
        route = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        route = previous_switch.beside
    else:
        return
    route.weight = inf


def get_time_max(previous_switch, current_switch):
    """
    Retourne le temps à partir duquel on considère une route comme coupée. On prend comme limite
    10 * le temps de parcours en conditions normales
    :param previous_switch: aiguillage précédent la route
    :param current_switch: aiguillage suivant la route
    :return: temps à partir duquel on considère une route comme coupée
    """
    if previous_switch.next.next == current_switch:
        route = previous_switch.next
    elif previous_switch.beside.next == current_switch:
        route = previous_switch.beside
    else:
        return -1
    return 10 * route.expected_weight
