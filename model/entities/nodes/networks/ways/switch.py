from .tracks.GestionnaireRevision import GestionnaireRevision
from ....tokens.pod import Pod
from .way import Way


class Switch(Way):
    """Classe mère des aiguillages sortant et entrant"""
    def __init__(self, env, id, margin_min, pod_size, max_speed, x=None, y=None, previous=None, next=None, beside=None, pods=None, id_bridge=None, **kwargs):
        super().__init__(env, id, pod_size, **kwargs)
        self._x = x or 0
        self._y = y or 0
        self._previous = previous
        self._next = next
        self._max_speed = max_speed
        self._speed = self._next.sections[0].speed
        self._beside = beside
        self._pods = pods or []
        self._id_bridge = id_bridge
        self._rules = []
        self._margin = self.speed * (margin_min + pod_size) / 8.33 - pod_size # Ce 8.33 est actuellement la vitesse minimal d'un réseau urbanloop en m/s (30 km/h) peut etre à changer

        # Ajout des capsules
        for pod in pods:
            speed = pod["speed"]
            distance = GestionnaireRevision.genererDistanceAleatoire() # à mettre dans json
            temps = GestionnaireRevision.genererTempsAleatoire() # à mettre dans json
            self._pods.append(Pod(env, self, speed, distance, temps, **pod))

        # Liaison des routes et sections de la boucle à l'aiguillage
        # Route précédente
        self._previous.next = self
        self._previous.sections[-1].next = self
        # Route suivante
        self._next.previous = self
        self._next.sections[0].previous = self

    @property
    def x(self):
        """Abscisse de l'aiguillage"""
        return self._x

    @property
    def y(self):
        """Ordonnée de l'aiguillage"""
        return self._y

    @property
    def margin(self):
        """Marge entre les capsules"""
        return self._margin

    @property
    def place_size(self):
        """Taille d'une place"""
        return self.pod_size + self.margin

    @property
    def beside(self):
        """Route du pont lié à l'aiguillage"""
        return self._beside

    @property
    def speed(self):
        """Vitesse moyenne au sein de l'aiguillage"""
        return self._speed

    @property
    def max_speed(self):
        """Vitesse maximale au sein de l'aiguillage en m/s"""
        return self._max_speed

    @property
    def next(self):
        """Route suivante de l'aiguillage (sur la même boucle)"""
        return self._next

    @property
    def previous(self):
        """Route précédente de l'aiguillage (sur la même boucle)"""
        return self._previous

    def is_destination(self):
        """Renvoie True s'il s'agit d'un switch vers/depuis une station/shed"""
        return len(self.beside.steps) >= 1

    def serialize(self):
        """Sérialise les information de l'aiguillage pour les envoyer à la vue"""
        dict = super().serialize()
        dict.update({
            "type": "switch",
            "pods": [pod.serialize() for pod in self.pods],
            "x": self.x,
            "y": self.y,
            "id_bridge": self.id_bridge,
            "speed": self.speed
        })
        return dict

    @property
    def pods(self):
        """Liste des capsules contenues dans l'aiguillage"""
        return self._pods

    @property
    def id_bridge(self):
        """Id du pont lié à l'aiguillage"""
        return self._id_bridge
