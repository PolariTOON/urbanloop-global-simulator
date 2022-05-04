from .GestionnaireRevision import GestionnaireRevision
from .....tokens.pod import Pod
from .step import Step


class Hangar(Step):
    """ Classe abstraite modélisant un dépôt, dont les classes descendantes remplacent Shed
    Y est géré le départ des capsules, le réapprovisionnement et
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
            "type": f"{self.__class__.__name__}",
            #"type": "shed",
            "pods": {
                "count": len(self.pods),
                "max": self.capacity
            },
            "departure_pods": departure_pods,
            "element_of_loop": self.element_of_loop
        })
        #print(f"\nDEBUT TEST HANGARS : Problèmes lors de jsonify")
        #print(f"Type : {self.__class__.__name__} - Nom : {self.name}")
        #print(f"departure_pods : ")
        #print(f"{departure_pods}")
        #print(f"FIN TEST HANGARS : Problèmes lors de jsonify\n")
        return dict

    @property
    def gestionnaireRevision(self):
        return self.parent.parent.gestionnaireRevision

    @property
    def gestionnaireLavage(self):
        return self.parent.parent.gestionnaireLavage

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
        pass

    @property
    def pods_during_departure(self):
        return [pod for pod in self._pods if pod.during_departure]

    def handle_message(self, message):
        pass
