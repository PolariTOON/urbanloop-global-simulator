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
                        if unvisited_switches.count(
                                chemin[i]) > 0:  # Si on a pas encore visité un noeud du chemin on lui associe une règle
                            change_loop = chemin[i - 1].beside.next == chemin[i]  # On regarde si on a changé de boucle
                            regle = Rule(chemin[i].elt.id, chemin[i].loop.id, elt, None, None,
                                         change_loop)  # TODO : à changer
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
                            new_rules.append(Rule(switches_list[i].elt.id, switches_list[i].loop.id, elt, None, None,
                                                  change_loop))  # TODO : à changer
                            unvisited_switches.remove(switches_list[i])  # TODO : à changer ?

        for shed in self._network.sheds:
            create_rules(shed)

        for station in self._network.stations:
            create_rules(station)
        return new_rules

    def drain_pod_station(self, station):
        """
        Libère une capsule vide de la station si elle est à 3/4 pleine
        La capsule est redirigée vers un dépôt
        :return: void
        """
        qsize = len(station.pods)
        if qsize < int(3 * station.capacity / 4):
            return
        pod = station.pods[0]
        if not pod.travelers:
            station.pods.remove(pod)
            pod.destination = self._network.get_random_free_shed()  # TODO : Prendre le dépôt le plus proche
            pod.priority = -1  # TODO : priorité à mettre à jour
            pod.travelers = None
            pod.source = station
            pod.position = 0
            pod.start_trip()  # TODO
            print(
                "La station %s s'est fait drainée une capsule vers le dépôt %s" % (station.name, pod.destination.name))

    def fill_and_full_stations(self):
        """
        Appel le controleur pour completer la station. On considère que la station est en situation critique si il ne
        reste aucune capsule disponible. La demande est alors effectué avec une priorité maximale(1). La capsule vide
        sera donc autant prioritaire qu'une capsule pleine. Si il reste au moins une capsule alors la demande est
        effectué avec une priorité faible
        """
        print("Complétion des stations")
        for station in self._network.stations:
            if len(station.pods) <= max(1, int(station.capacity / 4)):
                # quasi vide --> station à compléter
                simlog.debug("Station %s almost empty (caps_numb = %d)." % (station.name, len(station.pods)))
                if not station.pods:
                    self.refill(10, station)
                elif not station.capsule_arriving:
                    self.refill(6, station)
            if len(station.pods) >= min(station.capacity - 1, int(3 * station.capacity / 4)) and len(station.pods) > 1:
                # quasi pleine --> station à vider
                simlog.debug("Station %s almost full (caps_numb = %d, waiting travelers = %d)." % (
                    station.name, station.estimated_capsules_number(), station.traveler_queue.qsize()))
                self.drain_pod_station(station)

    def refill(self, prio, destination):
        """
        Réapprovisionne une station qui en effectue la demande
        :param prio: Priorité de la demande (10 si critique) OBLIGATOIRE
        :param destination: Station qui effectue la demande OBLIGATOIRE
        """
        shed = random.choice(self._network.sheds)  # TODO : à remplacer par le dépôt le plus proche
        if prio == 10:
            test = False
            for pod in self._network.pods:
                if len(pod.travelers) == 0 and pod.priority <= 6 and not pod.travelers:
                    test = True
                    trajet = shorter_way(next_switch(pod.track), next_switch(destination))
                    for i in range(len(trajet) - 1):
                        new_rules = []
                        change = trajet[i].beside.next == trajet[i + 1]
                        r = Rule(trajet[i].id, trajet[i + 1].loop.id, priority=10, empty=True,
                                 change=change)  # TODO : adapter le système de règles
                        new_rules.append(r)
                        self.send_list_rules(new_rules)  # TODO : adapter le système de règles
                if test:
                    break
            if test:
                if len(shed.pods) > 0:
                    drain_pod_shed(shed, destination, prio)
            else:
                if len(shed.pods) > 1:
                    drain_pod_shed(shed, destination, prio)
        else:
            if len(shed.pods) > 0:
                drain_pod_shed(shed, destination, prio)


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
    way = [(0, start_switch)]
    best_weight = {start_switch: 0}
    previouses = {}
    visited = set()
    while True:
        if way:
            entry = way.pop()
        else:
            break
        weight, switch = entry
        if switch not in visited:
            visited.add(switch)
            if switch == destination_switch:
                break
            # On a toujours le next comme successeur
            new_weight = weight + switch.next.weight
            min_weight = best_weight.get(switch.next.next)
            if min_weight is None or new_weight < min_weight:
                best_weight[switch.next.next] = new_weight
                previouses[switch.next.next] = switch
                way.append((new_weight, switch.next.next))
            if isinstance(switch, SwitchOut):  # Pour un out on a aussi le beside comme successeur
                new_weight = weight + switch.beside.weight
                min_weight = best_weight.get(switch.beside.next)
                if min_weight is None or new_weight < min_weight:
                    best_weight[switch.beside.next] = new_weight
                    previouses[switch.beside.next] = switch
                    way.append((new_weight, switch.beside.next))
    weight = best_weight.get(destination_switch)
    way = []
    if weight is not None:
        switch = destination_switch
        while switch is not None:
            way = [switch] + way
            switch = previouses.get(switch)
    return way


def drain_pod_shed(shed, destination, prio):
    """
    Libère une capsule vide du dépôt
    La capsule est redirigée vers une station
    :param shed: le dépôt à draîner
    :param destination: la station à alimenter
    :return: void
    """
    qsize = len(shed.pods)
    if qsize == 0:
        print("Plus de capsules disponibles dans le dépôt", shed.name)
        return
    pod = shed.pods[0]
    if not pod.travelers:
        shed.pods.remove(pod)
        pod.destination = destination
        pod.priority = prio  # TODO : priorité à mettre à jour
        pod.travelers = None
        pod.source = shed
        pod.position = 0
        pod.start_trip()  # TODO
        print("Une capsule part du dépôt %s vers la station %s" % (shed.name, destination.name))


def next_switch(track):
    """
    :param track: track dont on veut connaître le switch suivant le plus proche
    :return: L'aiguillage suivant le plus proche du track en entrée
    """
    current = track
    from model.networks.ways.switch import Switch
    while not isinstance(current, Switch):
        current = current.next
    return current

