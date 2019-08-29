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
        self._pods = [Pod(env, self, 0) for k in range(pods["count"])]
        self._capacity = pods["max"]
        self._element_of_loop = element_of_loop
        if departure_pods:
            for dico in departure_pods:
                p = dico["pod"]
                dico["pod"] = Pod(env, self, 0, p)
        self._departure_pods = departure_pods or []

    def serialize(self):
        """sérialise les informations du dépôt"""
        dict = super().serialize()
        dict.update({
            "type": "shed",
            "pods": {
                "count": len(self.pods),
                "max": self.capacity
            },
            "departure_pods": [{"pod": dico["pod"].serialize(), "destination": dico["destination"]} for dico in self._departure_pods]
        })
        return dict

    def to_element_of_loop(self):
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

    def update(self):
        """Fonction gérant le processus dépôt"""
        while True:
            if self._departure_pods\
                    and int((self.env.time - 1) % (self.next.margin / self.next.speed)) == 0:
                dico = self._departure_pods.pop(0)
                pod = dico["pod"]
                destination = dico["destination"]
                yield from pod.write({
                    "author": self,
                    "type": "departure",
                    "destination": destination
                })
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "  --  ", message["author"].name, "  --  ", message["type"])
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    pod = message["pod"]
                    yield from self._parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                    if pod.destination == self:
                        self._pods.append(pod)
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
                elif "refill" == message["type"]:
                    station = message["station"]
                    pod = self._pods[0]
                    self._pods.remove(pod)
                    self._departure_pods.append({"pod": pod, "destination": station})
                else:
                    raise ValueError("Invalid message")
