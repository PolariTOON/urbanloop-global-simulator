from .....tokens.pod import Pod
from .....tokens.traveler import Traveler
from .step import Step

station_types = {
    "city": 0,
    "residential": 1,
    "activity": 2,
}


class Station(Step):
    """ Classe modélisant une gare, y sont gérés le départ des capsules, le réapprovisionnement, la génération des voyageurs et leur montée
    dans les capsules, les échanges de messages avec les autres éléments du réseau"""
    def __init__(self, env, id, departure_pods=None, pods=None, travelers=None, boarding=None, departure_count=None, station_type=None, element_of_loop=None, parallel=None, **kwargs):
        super().__init__(env, id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        travelers = travelers or None  # attention travelers n'est pas un traveler de pod, il y a des informations supplémentaires
        station_type = station_type or station_types["city"]
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._average_waiting_time = 0
        self._waiting_times_since_last_minute = []
        self._failed_deviation_since_last_minute = 0
        self._all_time_count = 0
        self._travelers = []
        if travelers is not None:       # initialisation des travelers et dépendances
            self._average_waiting_time = travelers["average_waiting_time"]
            self._all_time_count = travelers["all_time_count"]
            if travelers["count"]:
                for _ in range(travelers["count"]):
                    self._travelers.append(Traveler(env, 0)) # todo pouvoir retrouver les temps d'attente quand on recharge le fichier pour ne pas fausser les stats (average_waiting_time) (ajouter dans serialize)
                                                             # pour le moment on génère de nouveaux travelers suivant le nombre qu'il y avait dans la station
        self._departure_count = departure_count or 0
        self._capacity = pods["max"]
        self._parallel = parallel or False  # il y a 2 configurations de stations : pods en série ou pods en parallèle
        self._boarding = boarding or [-1 for _ in range(self._capacity)]            # contient les temps d'attente liés aux embarquements
        self._station_type = station_type
        self._element_of_loop = element_of_loop
        self._pods = [None for _ in range(self._capacity)]
        for i in range(pods['count']):
            self._pods[-1-i] = Pod(env, self, 0)
        self._departure_pods = departure_pods or [] # pods en attente d'insertion dans le réseau
                                                    # TODO: revoir l'initialisation de departure_pods en cas de chargement reseau
        self._incoming_pods = 0  # à serialiser si on veut télécharger/recharger le réseau, c'est le nombre de pods en chemin vers la station
        self._waiting_empty = False # permet d'évacuer les pods superflus
        self.wait = -1 # pour décompter le départ entre 2 capsules

    def serialize(self):
        """Permet la serialisation des informations"""
        dict = super().serialize()
        #departure_pods = [{"pod": dico["pod"].serialize(), "destination": dico["destination"].serialize()} for dico in self._departure_pods]
        self.element_of_loop.update({
            "name": self.name
        })
        dict.update({
            "type": "station",
            "pods": {
                "count": self.pods_size,
                "max": self.capacity,
                "pos": [True if pod else False for pod in self._pods],
                "boarding": self._boarding,
                "full": [not pod.is_empty() if pod else False for pod in self._pods]
            },
            "travelers": {
                "count": len(self.travelers),
                "average_waiting_time": self.average_waiting_time,
                "all_time_count": self.all_time_count,
                "boarding_times": [pod.travelers[0].boarding_time if pod and not pod.is_empty() else None for pod in self._pods]
            },
            "departure_count": self._departure_count,
            "station_type": self.station_type,
            # "departure_pods": departure_pods,
            "element_of_loop": self.element_of_loop
        })
        return dict

    def up_all_time_count(self):
        self._all_time_count += 1

    def up_incoming_pods(self):
        self._incoming_pods += 1

    def down_incoming_pods(self):
        self._incoming_pods -= 1

    @property
    def pods_size(self):
         return len(self._pods) - self._pods.count(None)
        
    @property
    def element_of_loop(self):
        """Numéro de la gare parmis les éléments de la boucle"""
        return self._element_of_loop

    @property
    def name(self):
        """Nom de la gare"""
        return super().name or "Station %d" % self.id

    @property
    def average_waiting_time(self):
        """Temps d'attente moyen des voyageurs dans la gare"""
        return self._average_waiting_time

    @property
    def all_time_count(self):
        return self._all_time_count

    @property
    def pods(self):
        """
            Liste contenant les capsules arrêtées dans la station, SANS les None.
        """
        return [ pod for pod in self._pods if pod != None ]

    @property
    def travelers(self):
        """Liste modélisant les voyageurs en attente, elle contient leur temps d'attente"""
        return self._travelers

    @travelers.setter
    def travelers(self, value):
        self._travelers = value

    @property
    def station_type(self):
        """
            Type de la station
            0 : ville
            1 : résidentielle
            2 : activité
        """
        return self._station_type

    @property
    def capacity(self):
        return self._capacity

    def get_waiting_times_since_last_minute_and_reset(self):
        arr = self._waiting_times_since_last_minute
        self._waiting_times_since_last_minute = []
        return arr

    def get_failed_deviation_since_last_minute_and_reset(self):
        val = self._failed_deviation_since_last_minute
        self._failed_deviation_since_last_minute = 0
        return val

    def failed_deviation(self):
        self._failed_deviation_since_last_minute += 1

    def isFull(self):
        """
            Attention, on ne prend pas en compte les pods sur le point d'arriver
        """
        return self.pods_size < self._capacity

    def is_available(self):
        """
            Permet au SwitchOut menant à cette station de savoir
            s'il peut autoriser l'arrivée d'un pod
        """
        pods_almost_in_station = []
        # pods déjà sur le bridge
        pods_almost_in_station.extend(self.previous.pods)
        # pods sur le SwitchOut, ayant reçu l'autorisation de venir
        switchout = self.previous.previous
        for pod in switchout.pods:
            if pod.turn:
                pods_almost_in_station.append(pod)
        return self.pods_size + len(pods_almost_in_station) < self._capacity
    
    def send_pod(self, pod, destination, traveler=False):
        """
            Envoie une capsule.
            destination : nom de la station ou entrepôt où envoyer
            traveler : si la capsule doit contenir un voyageur ou non
        """
        for p in self._departure_pods:
            if p == pod:
                raise Exception(p.name[:8] + " already in departure pods")
        pod.destination = destination
        self._departure_pods.append(pod)

    def update(self):
        """Fonction gérant le processus gare"""
        #print(self._boarding)
        #print("%s  %d  %d  %d(%d)  %d" % (self.name,
        #                                  len(self._travelers),
        #                                  len([1 for t in self._boarding if t != -1]), # pods pour lesquels _boarding != -1
        #                                  len(self._departure_pods), len([p for p in self._departure_pods if p.is_empty()]),
        #                                  self.pods_size))

        # On charge les voyageurs s'il y a de la place
        if len(self._travelers) > 0 and self.pods_size > 0:
            for i in range(self._capacity-1, -1, -1):  # on commence par les premières capsules à partir
                pod = self._pods[i]
                if len(self._travelers) > 0 and pod != None and pod.is_empty() and pod not in self._departure_pods and not pod.during_departure:
                    # s'il y a un traveler en attente, un pod avec de la place
                    # IDEA : on pourrait autoriser un passager à utiliser une capsule vide qui allait partir (mais attention à ce que ça ne génère pas de bug)
                    going_traveler = self._travelers.pop(0)
                    going_traveler.departure(self.env.time)
                    pod.travelers = [going_traveler]
                    self._departure_count += 1
                    self._average_waiting_time = (  # calcul du temps d'attente moyen
                        (self._average_waiting_time * (self._departure_count - 1) + going_traveler.waiting_time) / self._departure_count
		    )
                    # On ajoute le nouveau temps d'attente dans la liste des temps d'attente de la derniere minute de la simulation
                    self._waiting_times_since_last_minute.append(going_traveler.waiting_time)
                    self._boarding[i] = 0  # début du décompte de l'embarquement
                else:
                    pass
        
        # Attente de la montée des voyageurs pour l'envoi d'une capsule
        for i in range(len(self._boarding)):  # pour chaque capsule
            if self._boarding[i] != -1:       # si un voyageur embarque
                self._boarding[i] += self.env.tick
                #
                # TODO : corriger bug :
                #        des fois, "self._pods[i]" est None ici (ça ne devrait pas être le cas)
                #        peut-être que ça arrive lorsqu'un pod arrive dans une station déjà pleine
                #
                if self._boarding[i] > self._pods[i].travelers[0].boarding_time:  # si le temps d'embarquement est atteint
                    destination = self._pods[i].travelers[0].destination
                    self._boarding[i] = -1  # reset du timer
                    self.send_pod(self._pods[i], destination, True)  # on l'ajoute à la liste des pods au départ

        # Attente entre le départ de 2 capsules
        if self.wait != -1:  # si une capsule est parti il y peu
            self.wait += self.env.tick
            if self.wait > self.next.margin / self.next.speed:
                self.wait = -1  # on peut de nouveau envoyer

        # Départ d'une capsule
        if self.wait == -1:  # wait == -1  =>  on peut de nouveau envoyer une capsule
            for pod0 in self._departure_pods:
                if pod0 not in self._pods:
                    print("\u001B[31mERROR: ", self.name, pod0.name[:8], "not in pods! (station l.207)\u001B[0m")
                    self._departure_pods.remove(pod0)

            pod = self._pods[-1]
            if pod is not None and pod in self._departure_pods:  # un pod attendait un départ
                self._departure_pods.remove(pod)
                destination = pod.destination
                traveler = None
                waiting_time = 0
                if pod.travelers:
                    traveler = pod.travelers[0]
                    waiting_time = traveler.waiting_time
                pod.during_departure = True
                pod.write({
                    "author": self,
                    "type": "departure",
                    "destination": destination
                })
                # prévient le parent
                self.parent.write({
                    "author": self,
                    "pod": pod,
                    "type": "departure",
                    "destination": destination,
                    "timestamp": self.env.time,
                    "waiting_time": waiting_time,
                    "traveler": traveler
                })
                self.wait = 0
            else:
                # si le pod est prêt à partir mais n'est pas en première position,
                # on peut vérifier que c'est bien parce qu'il attend le départ du premier pod.
                #first_pod = self._pods[0]
                #if len(self._departure_pods) > 0 and first_pod != None and not first_pod.during_departure and first_pod in self._departure_pods:
                #    print("WARNING: in station.py: a pod is ready to leave, but not in front position.")
                pass
            
        # On fait un appel pour libérer des capsules s'il y a trop de capsules vides en attente
        if not self._waiting_empty and self.need_empty():
            self._waiting_empty = True # TODO : remettre à False en cas de refus
                                       # (le refus n'est pas implémenté pour l'instant, mais pourrait l'être
                                       # s'il n'y a plus de places dans les sheds)
            # Vide la station de capsules
            self.parent.write({
                "author": self,
                "type": "empty",
                "station": self
            })
        
        if self.need_refill():
            # Ré-approvisionnement des capsules
            self.parent.write({
                "author": self,
                "type": "refill",
                "station": self.name
            })
            self.up_incoming_pods()  # un pod sera envoyé pour combler l'espace,
                                     # on incrémente ici pour éviter le spamming
                                     # des messages le temps que le pod soit envoyé
    
    def handle_message(self, message):
        if "pod_entry" == message["type"]:
            pod = message["pod"]
            self.parent.write({
                "author": self,
                "type": "pod_entry",
                "pod": pod
            })
            # la capsule va se garer dans la station s'il y a de la place
            if self._pods[0] is None:
                
                for i in range(len(self._pods)-1, -1, -1):
                    if self._pods[i] is None:
                        self._pods[i] = pod
                        break
                
                self._incoming_pods -= 1
                if self._incoming_pods < 0:
                    print("\033[4;31mERROR: mauvais comptage des incoming pods\u001B[0m",
			  self._incoming_pods, " ", self.name, "\n\t\t(station l.277)")

                if len(pod.travelers) > 0: 
                    pod.travelers[0].disembark()        # On fait stopper les updates de Traveler

                pod.travelers = []
                pod.write({
                    "author": self,
                    "type": "docked"
                })
                self.parent.write({
                    "author": self,
                    "type": "docked",
                    "pod": pod,
                    "timestamp": self.env.time
                })
            else:
                print("ERROR: La station %s ne devrait pas être pleine.\n\t\t(station l.333)" % self.name)
                pod.write({ # "passing" fait passer le pod à travers la station
                    "author": self,
                    "type": "passing"
                })
        
        elif "pod_exit" == message["type"]:
            self._waiting_empty = False  # pour autoriser à nouveau la libération de pods
            pod = message["pod"]
            if pod not in self.pods:
                # pod passing
                return
            pod.during_departure = False
            if pod != self._pods[-1]:
                print("ERROR: a pod left without being in the front position.\n\t\t(station l.327)")
            for i in range(self._capacity-1, 0, -1):  # on décale les autres pods vers l'avant
                #
                # TODO : ne pas faire ce décalage si un passager est en train de monter
                #        (sinon la capsule bouge pendant que la personne monte dedans...)
                #
                self._pods[i] = self._pods[i-1]
                self._boarding[i] = self._boarding[i-1]
            self._pods[0] = None
            self._boarding[0] = -1
        
        elif "empty" == message["type"]:
            pod = self._pods[-1]
            if pod is not None and self._boarding[-1] == -1 and not pod.during_departure and not pod in self._departure_pods:  # on libère un pod vide (pas None, n'a pas de passager et n'est pas déjà sur le point de partir)
                self.send_pod(pod, message["shed"].name)
                # "self._waiting_empty = False" est réalisé à la réception de "pod_exit"
            else:
                if pod is None:
                    print("\u001B[31mWARNING: ", self.name, ": pas de pod à libérer (station l.311)", len(self._departure_pods), "\u001B[0m")
                self._waiting_empty = False
            
        else:
            raise ValueError("Invalid message received by a station: ", message)

    def need_empty(self):
        """
            Permet de choisir si on se débarasse de capsules vides dans une station
        """
        if len(self._travelers) > 0 or len(self._departure_pods) > 0 or self._boarding.count(-1) < len(self._boarding):
            return False
        if self.capacity == 5:
            return self.pods_size - len(self._departure_pods) > 3
        elif self.capacity == 4:
            return self.pods_size - len(self._departure_pods) > 2
        elif self.capacity == 3:
            return self.pods_size - len(self._departure_pods) > 1
        elif self.capacity == 2:
            return self.pods_size - len(self._departure_pods) > 1
        elif self.capacity == 1:
            return self.pods_size - len(self._departure_pods) >= 1
        else:
            return self.pods_size - len(self._departure_pods) > self._pods_size/2

    def need_refill(self):
        """
            Permet d'appeler de nouvelles capsules s'il en manque dans la station
        """
        if self.capacity == 5:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 3
        elif self.capacity == 4:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 2
        elif self.capacity == 3:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 1
        elif self.capacity == 2:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 1
        elif self.capacity == 1:
            return False
        else:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 3
