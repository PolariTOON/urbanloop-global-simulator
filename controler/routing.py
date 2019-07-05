import random
from cmath import inf

from model.networks.network import Network
from settings import simlog
from stats.stats_recorder import StatsRecorder


class Routing:
    """
    Modélise le controleur global d'un réseau, en se rapprochant du paradigme SDN
    """
    def __init__(self, id, json_network):
        self._id = id
        self._network = Network(self._id, **json_network)  # Création du réseau à partir d'un fichier JSON
        self._rules = []
        self._recorder = StatsRecorder(0)  # TODO : Gérer les stats
        self._timers = [-1] * len(self._network.pods)  # TODO : Gérer les timers des capsules (temps de trajets)
        self._tab_depart = []  # TODO : Gérer les stats
        self._tab_temps = []  # TODO : Gérer les stats
        self._tab_depart_voy = []  # TODO : Gérer les stats
        self._tab_temps_voy = []  # TODO : Gérer les stats

        for route in self._network.routes:
            weight = 0
            for section in route.sections:
                weight += section.weight
            route.weight = weight

    # TODO : gérer les stats
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

    # TODO : gérer les stats
    def temps_moy_stat(self, id, temps):
        test = True
        for i in self._tab_depart:
            if i[0] == id:
                test = False
                self._tab_temps.append(temps - i[1])
                i[0] = -1
        if test:
            self._tab_depart.append([id, temps])

    # TODO : gérer les stats
    def temps_moy_voy_stat(self, id, temps):
        test = True
        for i in self._tab_depart_voy:
            if i[0] == id:
                test = False
                self._tab_temps_voy.append(temps - i[1])
                i[0] = -1
        if test:
            self._tab_depart_voy.append([id, temps])

    # TODO : gérer les stats
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

    # TODO : gérer les stats
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

    # TODO : gérer les stats
    def extract(self, simulated_time):
        self._recorder.stop_listen(simulated_time)
        self._recorder.extract()

    # TODO
    def update(self):
        """
        Appel l'update des éléments du modèle et gère les timers
        :return: void
        """
        self._network.update()

    def ascend_travelers(self, _env, second, probability, config, frequency):
        """
        Fait monter des voyageurs dans les capsules des stations, fonction appelée à chaque tick
        :param _env: environement simpy de la simulation
        :param second: temps simulé (= correspondant au temps réel) en seconde
        :param probability: instance de la classe probability propre à la simulation
        :param config: dictionnaire contenant la configuration du réseau
        :param frequency: nombre de ticks par seconde
        :return: déclenche des événements de monté de voyageurs dans les capsules des stations
        """
        trip_limit = int(config["TRAVELER"]["trip_limit"])
        for station in self._network.stations:
            if station.travelers and station.pods and (trip_limit > 0 or trip_limit == -1):
                if trip_limit != -1:
                    trip_limit -= 1
                if station.pods:
                    return

                station.travelers.pop(0)
                pod = station.pods[-1]
                destination = self._network.select_random_station(second, probability, departure_station=station)
                pod.add_traveler(destination)
                # sim_loop.recorder.add_waiting_time_traveler(traveler.get_waiting_seconds(), traveler) TODO : STATS A GENERER
                yield _env.process(ascent_event(station, pod, _env, config["TRAVELER"]["ascent_descent_duration"], frequency))

    def generate_travelers(self, traveler_limit, traveler_number, second, probability):
        """
        Génère un certain nombre de voyageurs répartis aléatoirement dans les stations
        :param traveler_limit: nombre maximum de voyageurs dans le réseau
        :param traveler_number: nombre de voyageurs à générer
        :param second: temps simulé (= correspondant au temps réel) en seconde
        :param probability: instance de la classe probability propre à la simulation
        :return: (void) génère un certain nombre de voyageurs
        """
        if not (traveler_limit > 0 or traveler_limit == -1):
            return
        for a_traveler in range(traveler_number):
            if traveler_limit != -1:
                traveler_limit -= 1
            source = self._network.select_random_station(second, probability)
            source.travelers.append(0)
            # self.temps_moy_voy_stat(self.id, sim_loop.get_simulated_time())  # TODO : STATS A GERER
            simlog.info("Traveler generated", source)

    def init_rules(self):
        """
        Initialise les règles liées au réseau, les règles sont propres à des aiguillages
        :return: (void)
        """
        def create_rules(elt, switches, rules):
            unvisited_switches = switches  # copie de tous les switchs
            while len(unvisited_switches) > 0:  # Tant qu'on a des switchs non visités
                for switch in unvisited_switches:
                    chemin = shorter_way(switch, elt)  # Calcul du plus court chemin entre le switch et end_node
                    for i in range(1, len(chemin)):
                        # Si on a pas encore visité un noeud du chemin on lui associe une règle
                        if unvisited_switches.count(chemin[i]) > 0:
                            change_loop = chemin[i - 1].beside.next == chemin[i]  # On regarde si on a changé de boucle
                            regle = Rule(chemin[i].elt.id, elt, None, None, change_loop)
                            rules.append(regle)
                            unvisited_switches.remove(chemin[i])

        # On créé des règle entre les switch et les garages/stations

        for shed in self._network.sheds:
            create_rules(shed, self._network.switches, self._rules)

        for station in self._network.stations:
            create_rules(station, self._network.switches, self._rules)

    def update_rules(self):
        """
        Met à jour les règles du réseau
        :return: la liste des règles du réseau mise à jour
        """
        new_rules = []

        def create_rules(elt, switches):
            unvisited_switches = switches
            while len(unvisited_switches) > 0:
                for switch in unvisited_switches:
                    switches_list = shorter_way(switch, elt)
                    for i in range(1, len(switches_list)):
                        if unvisited_switches.count(switches_list[i]) > 0:
                            change_loop = switches_list[i - 1].beside.next == switches_list[i]
                            new_rules.append(Rule(switches_list[i].elt.id, elt, None, None, change_loop))
                            unvisited_switches.remove(switches_list[i])

        for shed in self._network.sheds:
            create_rules(shed, self._network.switches.copy())

        for station in self._network.stations:
            create_rules(station, self._network.switches.copy())
        return new_rules

    def drain_pod_station(self, station):
        """
        Libère une capsule vide de la station si elle est à 3/4 pleine
        La capsule est redirigée vers un dépôt
        :param station: station à draîner
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
            pod.start_trip()  # TODO : le voyage d'une capsule
            print("Station %s : capsule draînée vers le dépôt %s" % (station.name, pod.destination.name))

    def fill_and_full_stations(self):
        """
        Appel le controleur pour completer la station. On considère que la station est en situation critique si il ne
        reste aucune capsule disponible. La demande est alors effectué avec une priorité maximale(1). La capsule vide
        sera donc autant prioritaire qu'une capsule pleine. Si il reste au moins une capsule alors la demande est
        effectué avec une priorité faible
        """
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
                    print("source:", type(pod.track), "||| destination:", destination.name)
                    trajet = shorter_way_tracks(pod.track, destination)
                    for i in range(len(trajet) - 1):
                        new_rules = []
                        change = trajet[i].beside.next == trajet[i + 1]
                        r = Rule(trajet[i].id, priority=10, empty=True, change=change)
                        new_rules.append(r)
                        self.send_list_rules(new_rules)
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

    def send_list_rules(self, r):
        """
        Envoie les règles aux aiguillages
        :param r: liste de règle à envoyer aux aiguillages
        :return: (void)
        """
        for rule in r:
            if self._rules.count(rule) == 0:
                self._rules.append(rule)
                for switch in self._network.switches:
                    switch.add_rule(rule)

    def send_all_rules(self):
        """
        Envoie toutes les règles du réseau aux aiguillages
        :return: (void)
        """
        for rule in self._rules:
            for switch in self._network.switches:
                switch.add_rule(rule)

    def replace_rules(self, r):
        """
        Remplace les règles des aiguillages
        :param r: liste de règle qui doivent remplacer les anciennes
        :return:
        """
        for rule in self._rules:
            if rule.priority is None:
                for switch in self._network.switches:
                    switch.remove_rule(rule)
                self._rules.remove(rule)
        for rule in r:
            if self._rules.count(rule) == 0:
                self._rules.append(rule)
                for switch in self._network.switches:
                    switch.add_rule(rule)


def ascent_event(station, pod, _env, ascent_descent_duration, frequency):
    """
    Evénement de monter d'un voyageur dans une capsule
    :param station: station dans laquelle un voyageur monte dans une capsule
    :param pod: capsule dans laquelle un voyageur monte
    :param _env: environnement simpy de la simulation
    :param ascent_descent_duration: temps moyen de monté et descente d'un voyageur dans/depuis une capsule
    :param frequency: nombre de ticks par seconde
    :return: Fait remonter l'événement de monté d'un voyageur dans une capsule
    """
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
    """
    Déclenche les fonctions qui modélisent la montée d'un voyageur dans une capsule
    C'est-à-dire le retrait de la capsule depuis la station dont elle part et le départ de la capsule
    :param station:
    :param pod:
    :return:
    """
    station.pods.remove(pod)
    pod.start_trip()  # TODO : départ d'une capsule


def update_weight(switch1, switch2, travel_time):
    """
    Met à jour le poids de la route reliant switch1 à switch2 qu'une capsule vient de parcourir
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


def shorter_way_tracks(start_track, destination_track):
    """
    Lance le calcul du plus court chemin si nécéssaire (i.e si les pistes sont sur des routes différentes)
    :param start_track: piste de départ
    :param destination_track: piste d'arrivée
    :return: liste d'aiguillages représentant le plus court chemin pour aller de star_switch à destination_switch
    Si elle est vie alors les pistes sont sur la même route
    """
    if previous_switch(start_track) == previous_switch(destination_track):
        return []
    else:
        return shorter_way(next_switch(start_track), previous_switch(destination_track))


def shorter_way(start_switch, destination_switch):
    """
    Calcul du plus court chemin entre deux aiguillages avec l'algorithme de Dijkstra
    :param start_switch: aiguillage de départ
    :param destination_switch: aiguillage d'arrivé
    :return: liste d'aiguillages représentant le plus court chemin pour aller de star_switch à destination_switch
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
    :param track: piste dont on veut connaître l'aiguillage suivant le plus proche
    :return: L'aiguillage suivant le plus proche du track en entrée
    """
    current = track
    from model.networks.ways.switch import Switch
    while not isinstance(current, Switch):
        current = current.next
    return current


def previous_switch(track):
    """
    :param track: piste dont on veut connaître le switch précédent le plus proche
    :return: L'aiguillage précédent le plus proche du track en entrée
    """
    current = track
    from model.networks.ways.switch import Switch
    while not isinstance(current, Switch):
        current = current.previous
    return current


class Rule:
    """
    Modélise les règles des aiguillages
    """
    def __init__(self, switch_id, destination=None, priority=None, empty=None, change=None):
        self.destination = destination
        self.priority = priority
        self.empty = empty
        self.switch_id = switch_id
        self.change = change

    def match(self, switch_id, destination=None, priority=None, empty=None):
        """
        :return: true if the rule matches
        """
        if switch_id == self.switch_id:
            if (destination is not None and destination == self.destination) or self.destination is None:
                if (priority is not None and priority == self.priority) or self.priority is None:
                    if (empty is not None and empty == self.empty) or self.empty is None:
                        return True
        return False
