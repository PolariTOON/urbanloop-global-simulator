from random import choice

from .....tokens.pod import Pod
from .....tokens.traveler import Traveler
from .step import Step
import datetime
import time
from controler import probability
from ast import literal_eval

station_types = {
    "city": 0,
    "residential": 1,
    "activity": 2,
}


class Station(Step):
    """ Classe modélisant une gare, y sont gérés le départ des capsules, le réapprovisionnement, la génération des voyageurs et leur montée
    dans les capsules, les échanges de messages avec les autres éléments du réseau"""
    def __init__(self, env, id, departure_pods=None, pods=None, travelers=None, departure_count=None, station_type=None, element_of_loop=None, parallel=None, **kwargs):
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
        self._parallel = parallel or False
        self._boarding = [-1 for _ in range(self._capacity)]            # contient les temps d'attente liés aux embarquements
        self._pods_ready = [False for _ in range(self._capacity)]       # contient un boolean indiquant si une capsule est prête à partir
        self._station_type = station_type
        self._element_of_loop = element_of_loop
        self._pods = [None for _ in range(self._capacity)]
        self._pods_size = 0
        self._departure_pods = departure_pods or []                     # dictionnaire des pods sur le point de partir
        for dico in self._departure_pods:
            p = dico["pod"]
            dest = self.find(dico["destination"])
            dico["pod"] = Pod(env, self, 0, p)
            dico["destination"] = dest
        self._incoming_pods = 0  # à serialiser si on veut télécharger/rechager le réseau, c'est le nombre de pods en chemin vers la station

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
                "boarding": [self._boarding[i] != -1 for i in range(self._capacity)],
                "full": [not pod.isEmpty() if pod else False for pod in self._pods]
            },
            "travelers": {
                "count": len(self.travelers),
                "average_waiting_time": self.average_waiting_time,
                "all_time_count": self.all_time_count,
                "boarding_times": [pod.travelers[0].boarding_time if pod and not pod.isEmpty() else None for pod in self._pods],  # todo vérifier à quoi ça sert et introduire les temps d'attente
            },
            "departure_count": self._departure_count,
            "station_type": self.station_type,
            # "departure_pods": departure_pods,
            "element_of_loop": self.element_of_loop
        })
        return dict

    def up_incoming_pods(self):
        self._incoming_pods += 1

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
        """Liste contenant les capsules arrêtée dans la station"""
        return self._pods

    @property
    def travelers(self):
        """Liste modélisant les voyageurs en attente, elle contient leur temps d'attente"""
        return self._travelers

    @travelers.setter
    def travelers(self, value):
        """setter de l'attribut traveler"""
        self._travelers = value

    @property
    def station_type(self):
        """type de la station
        0 : ville
        1 : résidentiel
        2 : activité"""
        return self._station_type

    @property
    def capacity(self):
        return self._capacity
        
    @property
    def pods_size(self):
        return sum(pod is not None for pod in self._pods)

    def isFull(self):
        return self._pods[0] != None

    def send_pod(self, pod, destination, traveler=False):
        """envoie une capsule
        destination : nom de la station ou entrepôt où envoyer
        traveler : si la capsule doit contenir un voyageur ou non
        """
        waiting_time = 0
        if traveler:
            waiting_time = pod.travelers[0].waiting_time
        self._departure_pods.append({
            "pod": pod,
            "destination": destination,
            "timestamp": self.env.time,
            "waiting_time": waiting_time,
            "traveler": traveler
        })

    def shift_pods(self, indice_du_pod_envoye):
        """Quand un pod est envoyé, on décale les autres pods vers l'avant"""
        for i in range(indice_du_pod_envoye, 0, -1):
            self._pods[i] = self._pods[i-1]
            self._boarding[i] = self._boarding[i-1]
            self._pods_ready[i] = self._pods_ready[i-1]
        self._pods[0] = None
        self._boarding[0] = -1
        self._pods_ready[0] = False

    def update(self):
        """Fonction gérant le processus gare"""
        wait = -1       # pour décompter le départ entre 2 capsules
        send_one_time = True
        while True:
            # On charge les voyageurs s'il y a de la place
            if len(self._travelers) > 0 and self.pods_size > 0:
                for i in range(self._capacity - 1, -1, -1):  # on commence par les premières capsules à partir
                    pod = self._pods[i]
                    if len(self._travelers) > 0 and pod and pod.isEmpty():  # s'il y a un traveler en attente, un pod avec de la place
                        going_traveler = self._travelers.pop(0)  # on enlève le traveler de ceux qui attendent
                        going_traveler.departure(self.env.time)  # heure de départ
                        pod.travelers = [going_traveler]         # le traveler est associé au pod
                        self._departure_count += 1               # on compte 1 départ de plus
                        self._average_waiting_time = (self._average_waiting_time * (self._departure_count - 1) + going_traveler.waiting_time) / self._departure_count  # calcul du temps d'attente moyen
                        self._boarding[i] = 0  # début du décompte de l'embarquement

            # Attente de la montée des voyageurs pour l'envoi d'une capsule
            for i in range(len(self._boarding)):  # pour chaque capsule
                if self._boarding[i] != -1:       # si un voyageur embarque
                    self._boarding[i] += self.env.tick  # on incrémente le temps
                    if self._boarding[i] > self._pods[i].travelers[0].boarding_time:  # si le temps d'embarquement est atteint
                        self._boarding[i] = -1  # reset du timer
                        self._pods_ready[i] = True   # on indique que le pod en position i est prêt à partir

            # Attente entre le départ de 2 capsules
            if wait != -1:                                          # une capsule se prépare au démarrage
                wait += self.env.tick                               # on décompte le départ
                if wait > self.next.margin / self.next.speed:       # quand on a assez attendu
                    wait = -1                                       # on peut envoyer la capsule
                    if self._parallel:  # si on est en parallèle, on peut envoyer n'importe quel pod
                        for i in self._pods_ready:
                            if i:
                                self.send_pod(self._pods[i], self._pods[i].travelers[0].destination, True)  # départ du pod
                                wait = -1
                    else:              # en série seul le premier pod peut partir
                        if self._pods_ready[-1]:
                            self.send_pod(self._pods[-1], self._pods[-1].travelers[0].destination, True)    # départ du pod
                            wait = -1


            # Départ d'une capsule
            if wait == -1:             # wait == -1 indique que l'on envoie une capsule
                wait = 0
                if len(self._departure_pods) > 0:
                    indice_pod = -1
                    for indice0 in range(len(self._pods_ready)-1, -1, -1):
                        if self._pods_ready[indice0]:
                            indice_pod = indice0
                            break
                    self.shift_pods(indice_pod)  # décalage des autres pods dans la file
                    dico = self._departure_pods.pop()
                    pod = dico["pod"]
                    destination = dico["destination"]
                    yield from pod.write({
                        "author": self,
                        "type": "departure",
                        "destination": destination
                    })
                    # prévient le parent
                    yield from self.parent.write({
                        "author": self,
                        "pod": pod,
                        "type": "departure",
                        "destination": destination,
                        "timestamp": dico["timestamp"],
                        "waiting_time": dico["waiting_time"],
                        "traveler": dico["traveler"]
                    })

            if self.pods_size < self._capacity / 2 \
                    and self._capacity * (3/4) > (self._incoming_pods + self.pods_size - len(self.travelers)) \
                    and self._capacity - 1 > (self._incoming_pods + self.pods_size - len(self.travelers)):
                # Re-approvisionnement des capsules
                yield from self.parent.write({
                    "author": self,
                    "type": "refill",
                    "station": self.name
                })
                self.up_incoming_pods()     # un pod sera envoyé pour combler l'espace,
                                            # on incrémente ici pour éviter le spamming
                                            # des messages le temps que le pod soit envoyé
            if self.pods_size > self._capacity - 1 and len(self._travelers) == 0 \
                    and len(self._departure_pods) == 0 and send_one_time:
                send_one_time = False
                # Vide la station de capsules
                yield from self.parent.write({
                    "author": self,
                    "type": "empty",
                    "station": self
                })
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    pod = message["pod"]
                    yield from self.parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                    # la capsule va se garer dans la station s'il y a de la place
                    if pod.destination == self.name and not self._pods[0]:
                        i = self.pods_size
                        if i < self.capacity:
                            self._pods[self.capacity - i -1] = pod
                            self._pods_size += 1
                            self._incoming_pods -= 1
                            if self._incoming_pods < 0:
                                print("\033[4;31merreur comptage incoming pods\u001B[0m", self._incoming_pods,
                                      "(station l.284)", self.name,"\n")
                        else:
                            raise Exception("pod entry but full station l.277")  # le pod vérifie déjà s'il peut s'insérer "not self.pods[0]"
                        pod.travelers = []
                        yield from pod.write({
                            "author": self,
                            "type": "docked"
                        })
                        yield from self.parent.write({
                            "author": self,
                            "type": "docked",
                            "pod": pod,
                            "timestamp": self.env.time
                        })
                    else:
                        yield from pod.write({
                            "author": self,
                            "type": "passing"
                        })
                elif "pod_exit" == message["type"]:
                    send_one_time = False
                elif "empty" == message["type"]:
                    if self._pods[-1]:
                        if self._boarding[-1] == -1:
                            self.send_pod(self._pods[-1], message["shed"].name)
                    pass
                else:
                    raise ValueError("Invalid message station l.306", message)
