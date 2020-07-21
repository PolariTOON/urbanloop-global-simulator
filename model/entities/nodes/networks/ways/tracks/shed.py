from .....tokens.pod import Pod
from .step import Step


class Shed(Step):
    """ Classe modélisant un dépôt, y est géré le départ des capsules, le réapprovisionnement et
    les interactions avec les autres éléments du réseau"""
    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._capacity = pods["max"]
        self._element_of_loop = element_of_loop
        self._pods = [Pod(env, self, 0) for k in range(pods["count"])]
        self._departure_pods = departure_pods or []
        for dico in self._departure_pods:  # pour initialiser des pods quand on charge un réseau
            p = dico["pod"]
            dico["pod"] = Pod(env, self, 0, p)
        self._wait = -1

    def serialize(self):
        """sérialise les informations du dépôt"""
        dict = super().serialize()
        departure_pods = [{"pod": pod.serialize(), "destination": pod.destination} for pod in self._departure_pods]
        self.element_of_loop.update({
            "name": self.name
        })
        dict.update({
            "type": "shed",
            "pods": {
                "count": len(self.pods),
                "max": self.capacity
            },
            "departure_pods": departure_pods,
            "element_of_loop": self.element_of_loop
        })
        return dict

    @property
    def element_of_loop(self):
        """Retourne le numéro du dépôt au sein des éléments de sa boucle"""
        return self._element_of_loop

    @property
    def name(self):
        """Nom du dépôt"""
        return super().name or "Shed %d" % self.id

    @property
    def pods(self):
        """Liste des capsules stockées dans le dépôt"""
        return self._pods

    @property
    def capacity(self):
        """Capacité d'accueil maximale du dépôt"""
        return self._capacity

    def isFull(self):
        return self._capacity - len(self._pods) == 0

    def update(self):
        """Fonction gérant le processus dépôt"""
        while True:
            # Attente pour le prochain départ
            if self._wait != -1:
                self._wait += self.env.tick
                if self._wait > self.next.margin / self.next.speed:
                    self._wait = -1

            # Départ d'une capsule
            if self._departure_pods and self._wait == -1:
                self._wait = 0
                pod = self._departure_pods.pop(0)
                destination = pod.destination
                print(">>>", pod.name, "message departure")
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
                    "timestamp": self.env.time,
                    "waiting_time": 0,
                    "traveler": False
                })
                print("remove ", pod.name)
                self._pods.remove(pod)

            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    pod = message["pod"]
                    yield from self._parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                    if pod.destination == self.name:
                        self._pods.append(pod)
                        print("pods en stock :", self.name, len(self._pods), "(shed l.116)")
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
                    pass
                elif "refill" == message["type"]:
                    station = message["station"]
                    if len(self._pods) > 0:
                        i = 0
                        while self._pods[i] in self._departure_pods:
                            i += 1
                        pod = self._pods[i]
                        pod.destination = station
                        self._departure_pods.append(pod)
                        print(">> add ", pod.name)
                    else:
                        print("\u001B[31m", self.name, "envoie de pod impossible, shed vide", len(self._pods), "\u001B[0m", "(shed l.141)\n")
                        for station0 in self.parent.parent.stations:
                            if station0.name == station:
                                station0._incoming_pods -= 1
                else:
                    raise ValueError("Invalid message")
