"""
réuni des connexions pour former les switchs du réseau
"""
from ..tokens.pod import Pod
from .way import Way


class Switch(Way):
    def __init__(self, env, id, x=None, y=None, previous=None, next=None, beside=None, pods=None, id_bridge=None, **kwargs):
        super().__init__(env, id, **kwargs)
        self._x = x or 0
        self._y = y or 0
        self._previous = previous
        self._next = next
        self._beside = beside
        self._pods = []
        self._id_bridge = id_bridge
        self._rules = []
        self._margin = 2
        self._pod_size = 2

        # Ajout des capsules
        for pod in pods:
            self._pods.append(Pod(env, self, pod["speed"], False, **pod))

        # Liaison des routes et sections de la boucle à l'aiguillage
        # Route précédente
        self._previous.next = self
        self._previous.sections[-1].next = self
        # Route suivante
        self._next.previous = self
        self._next.sections[0].previous = self

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def beside(self):
        return self._beside

    @property
    def next(self):
        return self._next

    @property
    def previous(self):
        return self._previous

    @property
    def average_speed(self):
        return self._beside.sections[0].speed

    @property
    def limit_speed(self):
        return 22.7

    @property
    def d_min(self):
        return self._pod_size + self._margin

    def add_rule(self, rule):
        if self._rules.count(rule) == 0:
            self._rules.insert(0, rule)

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "switch",
            "pods": [pod.serialize() for pod in self._pods],
            "x": self._x,
            "y": self._y,
            "id_bridge": self._id_bridge
        })
        return dict

    @property
    def pods(self):
        return self._pods
