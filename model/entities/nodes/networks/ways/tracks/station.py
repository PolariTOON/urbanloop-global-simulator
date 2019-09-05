from .....tokens.pod import Pod
from .step import Step

station_types = {
    "city": 0,
    "residential": 1,
    "activity": 2,
}


class Station(Step):
    """ Classe modélisant une gare, y est géré lé départ des capsules, le réapprovisionnement, la génération des voyageurs et leur montée
    dans les capsules, les échanges de messages avec les autres éléments du réseau"""
    def __init__(self, env, id, departure_pods=None, pods=None, travelers=None, station_type=None, element_of_loop=None, **kwargs):
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
        self._pods = [Pod(env, self, 0) for k in range(pods["count"])]
        self._capacity = pods["max"]
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
            dico["destination"] = self.find(dest)

    def serialize(self):
        """Permet la serialisation des informations"""
        dict = super().serialize()
        departure_pods = [{"pod": dico["pod"].serialize(), "destination": dico["destination"]} for dico in self._departure_pods]
        dict.update({
            "type": "station",
            "pods": {
                "count": len(self.pods),
                "max": self.capacity
            },
            "travelers": {
                "count": len(self.travelers),
                "average_waiting_time": self.average_waiting_time,
                "all_time_count": self.all_time_count
            },
            "station_type": self.type,
            "departure_pods": departure_pods,
            "element_of_loop": self._element_of_loop
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
    def type(self):
        """type de la station
        0 : ville
        1 : résidentiel
        2 : activité"""
        return self._station_type

    @property
    def capacity(self):
        return self._capacity

    def update(self):
        """Fonction gérant le processus gare"""
        refill = False
        while True:
            if self._departure_pods and int((self.env.time - 1) % (self.next.margin / self.next.speed)) == 0:
                dico = self._departure_pods.pop(0)
                pod = dico["pod"]
                destination = dico["destination"]
                yield from pod.write({
                    "author": self,
                    "type": "departure",
                    "destination": destination
                })
            if len(self._pods) < self._capacity / 3 and not refill:
                # Re-approvisionnement des capsules
                refill = True
                yield from self.parent.write({
                    "author": self,
                    "type": "refill",
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
                    if pod.destination == self and len(self._pods) < self._capacity:
                        self._pods.append(pod)
                        refill = False
                        yield from pod.write({
                            "author": self,
                            "type": "docked"
                        })
                        yield from self.parent.write({
                            "author": self,
                            "type": "docked",
                            "pod": pod
                        })
                    else:
                        yield from pod.write({
                            "author": self,
                            "type": "passing"
                        })
                elif "pod_exit" == message["type"]:
                    pass
                else:
                    raise ValueError("Invalid message")
