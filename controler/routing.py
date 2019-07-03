"""
C'est ici qu'est le controler du paradigme SDN (calcul des routes ...)
"""
import random
from cmath import inf

from model.networks.network import Network
from model.rule import Rule
from settings import simlog
from stats.stats_recorder import StatsRecorder


class Routing:
    def __init__(self, id, json_network, config):
        self._id = id
        self._network = Network(self._id, **json_network)
        self._recorder = StatsRecorder(0)  # TODO : à déplacer ici
        self._timers = [-1] * len(self._network.pods)
        self._tab_depart = []
        self._tab_temps = []
        self._tab_depart_voy = []
        self._tab_temps_voy = []
        self._rules = []  # TODO : à changer ?
        self._timer_other = int(config.routing['timer_other'])
        self._my_timer = int(config.routing['my_timer'])
        self._switched_cost = int(config.routing['switched_cost'])
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
        """
        Appel l'update des éléments du modèle et gère les timers
        :return: void
        """
        self._network.update()

    def ascend_travelers(self, _env, config, frequency):
        trip_limit = config["TRAVELER"]["trip_limit"]
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

    def init_rules(self):
        def create_rules(elt):
            unvisited_switches = self._network.switches.copy()  # copie de tous les switchs
            while len(unvisited_switches) > 0:  # Tant qu'on a des switchs non visités
                for switch in unvisited_switches:
                    chemin = shorter_way(switch, elt)  # Calcul du plus court chemin entre le switch et end_node
                    for i in range(1, len(chemin)):
                        if unvisited_switches.count(chemin[i]) > 0:  # Si on a pas encore visité un noeud du chemin on lui associe une règle
                            change_loop = chemin[i - 1].beside.next == chemin[i]  # On regarde si on a changé de boucle
                            regle = Rule(chemin[i].elt.id, chemin[i].loop.id, elt, None, None, change_loop)  # TODO : à changer
                            self._rules.append(regle)  # TODO : à changer ?
                            unvisited_switches.remove(chemin[i])

        # On créé des règle entre les switch et les garages/stations

        for shed in self._network.sheds:
            create_rules(shed)

        for station in self._network.stations:
            create_rules(station)

    def update_rules(self):
        new_rules = []

        def create_rules(elt):
            unvisited_switches = self._network.switches.copy()
            while len(unvisited_switches) > 0:
                for switch in unvisited_switches:
                    switches_list = shorter_way(switch, elt)
                    for i in range(1, len(switches_list)):
                        if unvisited_switches.count(switches_list[i]) > 0:
                            change_loop = switches_list[i - 1].beside.next == switches_list[i]
                            new_rules.append(Rule(switches_list[i].elt.id, switches_list[i].loop.id, elt, None, None, change_loop))  # TODO : à changer
                            unvisited_switches.remove(switches_list[i])  # TODO : à changer ?

        for shed in self._network.sheds:
            create_rules(shed)

        for station in self._network.stations:
            create_rules(station)
        return new_rules


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


def shorter_way(start_switch, destination_switch):
    """
    Calcul du plus court chemin entre deux aiguillages avec l'algorithme de Dijkstra
    :param start_switch: aiguillage de départ
    :param destination_switch: aiguillage d'arrivé
    :return: liste de routes représentant le plus court chemin pour aller de star_switch à destination_switch
    """
    from model.networks.ways.switch_out import SwitchOut
    from model.networks.ways.switch_in import SwitchIn
    way = [(0, start_switch)]
    best_weight = {start_switch: 0}
    previouses = {}
    visited = set()
    while True:
        entry = way.pop()
        if entry is None:
            break
        weight, switch = entry
        if switch not in visited:
            visited.add(switch)
            if switch == destination_switch:
                break
            if switch is SwitchOut or switch is SwitchIn:  # On a toujours le next comme successeur
                new_weight = weight + switch.next.weight
                min_weight = best_weight.get(switch.next.next)
                if min_weight is None or new_weight < min_weight:
                    best_weight[switch.next.next] = new_weight
                    previouses[switch.next.next] = switch
                    way.append((new_weight, switch.next.next))
            if switch is SwitchOut:  # Pour un out on a aussi le beside comme successeur
                new_weight = weight + switch.beside.weight
                min_weight = best_weight.get(switch.beside.next)
                if min_weight is None or new_weight < min_weight:
                    best_weight[switch.beside.next] = new_weight
                    previouses[switch.beside.next] = switch
                    way.append((new_weight, switch.beside.next))
    weight = best_weight.get(destination_switch)
    way = []
    if weight is not None:
        switch = start_switch
        while switch is not None:
            way = [switch] + way
            switch = previouses.get(switch)
    return way

