from random import choice

from .....tokens.pod import Pod
from .....tokens.traveler import Traveler
from .step import Step
import datetime
import time
from controler import probability

station_types = {
    "city": 0,
    "residential": 1,
    "activity": 2,
}


class Station(Step):
    """ Classe modélisant une gare, y est géré lé départ des capsules, le réapprovisionnement, la génération des voyageurs et leur montée
    dans les capsules, les échanges de messages avec les autres éléments du réseau"""
    def __init__(self, env, id, departure_pods=None, pods=None, travelers=None, departure_count=None, station_type=None, element_of_loop=None, parallel=None, **kwargs):
        super().__init__(env, id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        travelers = travelers or 0
        station_type = station_type or station_types["city"]
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._average_waiting_time = travelers["average_waiting_time"] or 0
        self._all_time_count = travelers["all_time_count"] or 0
        self._departure_count = departure_count or 0
        #self._capacity = pods["max"]
        self._capacity = 4
        self._pods = [None for _ in range(self._capacity)]
        self._parallel = parallel or False
        self._boarding = [-1 for _ in range(self._capacity)]
        if travelers["count"]:
            self._travelers = [self._average_waiting_time in range(travelers["count"])]
        else:
            self._travelers = []
        self._station_type = station_type
        self._element_of_loop = element_of_loop
        self._departure_pods = departure_pods or []
        for dico in self._departure_pods:
            p = dico["pod"]
            dest = self.find(dico["destination"])
            dico["pod"] = Pod(env, self, 0, p)
            dico["destination"] = dest

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
                "boarding_times": [pod.travelers[0].boarding_time if pod and not pod.isEmpty() else None for pod in self._pods],
            },
            "departure_count": self._departure_count,
            "station_type": self.station_type,
            #"departure_pods": departure_pods,
            "element_of_loop": self.element_of_loop
        })
        return dict

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
        return self._capacity - self.pods_size == 0

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
        pod.ready = True       

    def update(self):
        """Fonction gérant le processus gare"""
        refill = False
        empty = False
        wait = -1
        forward = [-1 for _ in range(self._capacity - 1)]
        while True:
            # On envoie les voyageurs au hasard s'il y a de la place
            if len(self._travelers) > 0 and self.pods_size > 0:
                for i in range(self._capacity - 1, -1, -1):
                    pod = self._pods[i]
                    if pod and pod.isEmpty() and (i == self._capacity-1 or forward[i] == -1):
                        going_traveler = self.travelers.pop(0)
                        going_traveler.departure(self.env.time)
                        pod.travelers = [going_traveler]
                        self._departure_count += 1
                        self._average_waiting_time = (self._average_waiting_time * (self._departure_count - 1) + going_traveler.waiting_time) / self._departure_count
                        self._boarding[self._pods.index(pod)] = 0

            # Attente de la montée du voyageur pour l'envoi d'une capsule
            for i in range(len(self._boarding)):
                if self._boarding[i] != -1:
                    self._boarding[i] += self.env.tick
                    if self._boarding[i] > self._pods[i].travelers[0].boarding_time:
                        stations = self._parent.parent.stations_names
                        stations.remove(self.name)
                        name = choice(stations)
                        while name == self.name:
                            name = chose(stations)
                        self.send_pod(self._pods[i], self.find({"name": name}), True)
                        self._boarding[i] = -1

            # Attente pour le prochain départ
            if wait != -1:
                wait += self.env.tick
                if wait > self.next.margin / self.next.speed:
                    wait = -1
             
            # En parallèle pas d'avancement dans les places
            if not self._parallel:
                # Les capsules avancent dans les places 
                for i in range(self._capacity - 1):
                    if self._pods[i] and not self._pods[i+1] and forward[i] == -1 and self._boarding[i] == -1:
                        forward[i] = 0

                # Attente pour continuer d'avancer dans les places
                for i in range(len(forward)):
                    if forward[i] != -1:
                        forward[i] += self.env.tick
                        if forward[i] > 2:
                            self._pods[i+1] = self._pods[i]
                            self._pods[i] = None
                            forward[i] = -1

            # Départ d'une capsule
            if wait == -1:
                wait = 0
                for i in range(self._capacity):
                    if (i == self._capacity-1 or self._parallel) and self._pods[i] and self._pods[i].ready:
                        self._pods[i] = None
                        dico = self._departure_pods.pop()
                        pod = dico["pod"]
                        pod.ready = False
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

            if not refill and self.pods_size < self._capacity / 2:
                # Re-approvisionnement des capsules
                refill = True
                yield from self.parent.write({
                    "author": self,
                    "type": "refill",
                    "station": self
                })
                
            if not empty and self.pods_size > self._capacity / 2 and len(self._travelers) == 0:
                # Vide la station de capsules
                empty = True
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
                    if pod.destination == self and self.pods_size < self._capacity:
                        self._pods[0] = pod
                        pod.travelers = []
                        refill = False
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
                    empty = False
                elif "empty" == message["type"]:
                    if self._pods[-1]:
                        if self._boarding[-1] == -1 and forward[-1] == -1:
                            self.send_pod(self._pods[-1], message["shed"])
                    else:
                        empty = False
                    pass;
                else:
                    raise ValueError("Invalid message")
