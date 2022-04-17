from .GestionnaireRevision import GestionnaireRevision
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
        return len(self._pods) == self._capacity

    def is_available(self):
        return len(self._pods) < self._capacity

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
            pod.during_departure = True
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

    @property
    def pods_during_departure(self):
        return [pod for pod in self._pods if pod.during_departure]

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
                pod.during_departure = False
            else:
                # dans ce cas, le pod n'était pas docked dans le shed,
                # et on accepte qu'il passe à travers.
                pass
        elif "refill" == message["type"]:
            station = message["station"]
            if len(self._pods) > 0 and len(self._pods) > len(self._departure_pods) + len(self.pods_during_departure):  # on vérifie qu'il y a des pods et qu'il ne s'agit pas de pods déjà affectés à une station
                i = 0
                while i < len(self._pods) - 1 and (self._pods[i] in self._departure_pods or self._pods[i].during_departure):
                    i += 1
                pod = self._pods[i]
                pod.destination = station
                self._departure_pods.append(pod)
            else:
                # on cherche la station concernée,
                # et on l'informe qu'elle ne recevra pas le pod.
                network = self.parent.parent
                found_station = network.get_station_by_name(station)
                found_station.down_incoming_pods()

        else:
            raise ValueError("Invalid message")
