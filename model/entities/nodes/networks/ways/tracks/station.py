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
            self._pods[-i-1] = Pod(env, self, 0)
        self._departure_pods = departure_pods or [] # pods en attente d'insertion dans le réseau
                                                    # TODO: revoir l'initialisation de departure_pods en cas de chargement reseau
        self._incoming_pods = 0  # à serialiser si on veut télécharger/recharger le réseau, c'est le nombre de pods en chemin vers la station
        self.send_one_time = True # permet d'évacuer les pods superflus
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
                "full": [not pod.isEmpty() if pod else False for pod in self._pods]
            },
            "travelers": {
                "count": len(self.travelers),
                "average_waiting_time": self.average_waiting_time,
                "all_time_count": self.all_time_count,
                "boarding_times": [pod.travelers[0].boarding_time if pod and not pod.isEmpty() else None for pod in self._pods]
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
        """Liste contenant les capsules arrêtées dans la station"""
        return self._pods

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
        if pod is None:
            raise Exception("Can't send None, need a pod")
        pod.destination = destination
        self._departure_pods.append(pod)

    def shift_pods(self, indice_du_pod_envoye):
        """Quand un pod est envoyé, on décale les autres pods vers l'avant
         le pod envoyé est placé en première position pour que la voie suivante intègre
         le pod en même temps que le pod soit enlevé"""
        if indice_du_pod_envoye < 1:
            return

        pod = self._pods[indice_du_pod_envoye]
        for i in range(indice_du_pod_envoye, 0, -1):
            self._pods[i] = self._pods[i-1]
            self._boarding[i] = self._boarding[i-1]
        self._pods[0] = pod     # la suppression se fait en même temps que l'arrivée sur la voie suivante pour pouvoir
                                # suivre le nombre de capsule dans le réseau, suppression section l.121 (pod[0] = None)
        self._boarding[0] = -1

    def update(self):
        """Fonction gérant le processus gare"""
        
        # On fait un appel pour libérer des capsules s'il y a trop de capsules vides en attente
        if self.send_one_time and self.need_empty():
            self.send_one_time = False
            # Vide la station de capsules
            self.parent.write({
                "author": self,
                "type": "empty",
                "station": self
            })

        # On charge les voyageurs s'il y a de la place
        if len(self._travelers) > 0 and self.pods_size > 0:
            for i in range(self._capacity - 1, -1, -1):  # on commence par les premières capsules à partir
                pod = self._pods[i]
                if len(self._travelers) > 0 and pod and pod.isEmpty() and pod not in self._departure_pods:  # s'il y a un traveler en attente, un pod avec de la place
                    # TODO :  autoriser un passager à utiliser une capsule vide qui allait partir
                    going_traveler = self._travelers.pop(0)  # on enlève le traveler de ceux qui attendent
                    going_traveler.departure(self.env.time)  # heure de départ
                    pod.travelers = [going_traveler]         # le traveler est associé au pod
                    self._departure_count += 1               # on compte 1 départ de plus
                    self._average_waiting_time = (self._average_waiting_time * (self._departure_count - 1) + going_traveler.waiting_time) / self._departure_count  # calcul du temps d'attente moyen
                    # On ajoute le nouveau temps d'attente dans la liste des temps d'attente de la derniere minute de la simulation
                    self._waiting_times_since_last_minute.append(going_traveler.waiting_time)
                    self._boarding[i] = 0  # début du décompte de l'embarquement

        # Attente de la montée des voyageurs pour l'envoi d'une capsule
        for i in range(len(self._boarding)):  # pour chaque capsule
            if self._boarding[i] != -1:       # si un voyageur embarque
                self._boarding[i] += self.env.tick  # on incrémente le temps
                #
                # TODO : corriger bug :
                #        des fois, "self._pods[i]" est None ici (ça ne devrait pas être le cas)
                #        peut-être que ça arrive lorsqu'un pod arrive dans une station déjà pleine
                #
                if self._boarding[i] > self._pods[i].travelers[0].boarding_time:  # si le temps d'embarquement est atteint
                    destination = self._pods[i].travelers[0].destination
                    self._boarding[i] = -1  # reset du timer
                    self._pods[i].ready = True   # on indique que le pod en position i est prêt à partir
                    self.send_pod(self._pods[i], destination, True)  # on l'ajoute à la liste des pods au départ

        # Attente entre le départ de 2 capsules
        if self.wait != -1:                                          # une capsule est parti il y peu
            self.wait += self.env.tick                               # on décompte le départ
            if self.wait > self.next.margin / self.next.speed:       # quand on a assez attendu
                self.wait = -1                                       # on peut envoyer

        # Départ d'une capsule
        if self.wait == -1:  # wait == -1 indique que l'on peut de nouveau envoyer une capsule
            for pod0 in self._departure_pods:   # normalement les pods de departure_pods sont ceux qui attendent
                                                # de partir et doivent donc etre dans pods
                if pod0 not in self.pods:
                    print("\u001B[31m", self.name, pod0.name[:8], "not in pods! (station l.207)\u001B[0m")
                    self._departure_pods.remove(pod0)
            if len(self._departure_pods) > 0:  # un pod attendait un départ
                pod = self._departure_pods.pop(0)
                indice_pod = self.pods.index(pod)   # indice du pod qui doit partir
                self.shift_pods(indice_pod)  # décalage des autres pods dans la file
                pod.ready = False
                destination = pod.destination
                traveler = None
                waiting_time = 0
                if pod.travelers:
                    traveler = pod.travelers[0]
                    waiting_time = traveler.waiting_time
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
            if pod.destination == self.name and not self._pods[0]:
                #
                # TODO : comprendre la gestion des pods dans Station
                #
                if self.pods_size < self.capacity:
                    for i in range(len(self.pods)-1, -1, -1):
                        if self._pods[i] is None:
                            self._pods[i] = pod
                            break
                    self._incoming_pods -= 1
                    if self._incoming_pods < 0:
                        print("\033[4;31merreur comptage incoming pods\u001B[0m", self._incoming_pods,
                              "(station l.277)", self.name, "\n")
                else:
                    raise Exception("pod entry but full station l.277")  # le pod vérifie déjà s'il peut s'insérer "not self.pods[0]"
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
                pod.write({
                    "author": self,
                    "type": "passing"
                })
        elif "pod_exit" == message["type"]:
            self.send_one_time = True  # pour autoriser à nouveau la libération de pods
            if message["pod"] in self._departure_pods:
                self._departure_pods.remove(message["pod"])  # lorsqu'une capsule part suite à un appel "empty", il faut la supprimer de departure_pods
            if message["pod"] in self._pods:
                index = self._pods.index(message["pod"])
                self._pods[index] = None
                # TODO : enlever le print ci-dessous
                #print("Info: pod index in station: %d" % index)
        elif "empty" == message["type"]:
            for i in range(len(self._pods) - 1, -1, -1):
                if self._pods[i] is not None and self._boarding[i] == -1 and not self._pods[i].ready:  # on libère un pod vide (pas None, n'a pas de passager et n'est pas déjà sur le point de partir)
                    if self._pods[i] not in self._departure_pods:
                        self.send_pod(self._pods[i], message["shed"].name)
                        wait = -1
                        break
                else:
                    print("\u001B[31m", self.name, "pas de pod à libérer (station l.311)", len(self._departure_pods), "\u001B[0m")
            self.send_one_time = True  # pour autoriser un autre message empty
            
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
        elif self.capacity <= 3:
            return self.pods_size - len(self._departure_pods) > 1
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
        elif self.capacity <= 3:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 1
        else:
            return self._incoming_pods + self.pods_size - len(self.travelers) - len(self._departure_pods) < 3
