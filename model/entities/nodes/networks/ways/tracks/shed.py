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
    def pods_size(self):
        """Liste des capsules stockées dans le dépôt"""
        return len(self._pods)

    @property
    def capacity(self):
        """Capacité d'accueil maximale du dépôt"""
        return self._capacity

    def isFull(self):
        return self._capacity - len(self._pods) == 0

    @property
    def updatable(self):
        return True
    
    def update(self):
        """Fonction gérant le processus dépôt"""
        
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
                "waiting_time": 0,
                "traveler": False
            })

    def handle_message(self, message):
        if "pod_entry" == message["type"]:
            pod = message["pod"]
            self._parent.write({
                "author": self,
                "type": "pod_entry",
                "pod": pod
            })
            if pod.destination == self.name:
                self._pods.append(pod)
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
            pod = message["pod"]
            if pod in self._pods:
                self._pods.remove(pod)
            else:
                # dans ce cas, le pod n'était pas docked dans le shed,
                # et on accepte qu'il passe à travers.
                pass
        elif "refill" == message["type"]:
            station = message["station"]
            if len(self._pods) > 0 and len(self.pods) > len(self._departure_pods):  # on vérifie qu'il y a des pods et qu'il ne s'agit pas de pods déjà affectés à une station
                i = 0
                while i < len(self._pods) - 1 and self._pods[i] in self._departure_pods:
                    i += 1
                pod = self._pods[i]
                pod.destination = station
                self._departure_pods.append(pod)
            else:
                # print("\u001B[31m", self.name, "envoie de pod impossible, shed vide", len(self._pods), "\u001B[0m", "(shed l.141)\n")
                #
                # TODO : corriger ça ??!! (il faut juste décrémenter incoming_pods pour UNE station)
                #
                for station0 in self.parent.parent.stations:
                    if station0.name == station:
                        station0._incoming_pods -= 1
        else:
            raise ValueError("Invalid message")
