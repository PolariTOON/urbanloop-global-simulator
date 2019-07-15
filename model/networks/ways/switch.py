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
        self._pods_previous = []
        self._pods_next = []
        self._pods_beside = []
        self._id_bridge = id_bridge
        self._rules = []

        # Ajout des capsules
        for key in pods:
            pods_key = pods[key]
            for pod in pods_key:
                if key == "loop_in":
                    self._pods_previous.append(Pod(env, self, **pod))
                elif key == "loop_out":
                    self._pods_next.append(Pod(env, self, **pod))
                else:
                    self._pods_beside.append(Pod(env, self, **pod))

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

    def add_rule(self, rule):
        if self._rules.count(rule) == 0:
            self._rules.insert(0, rule)

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "switch",
            "pods": {
                "previous": [pod.serialize() for pod in self._pods_previous],
                "next": [pod.serialize() for pod in self._pods_next],
                "beside": [pod.serialize() for pod in self._pods_beside]
            },
            "x": self._x,
            "y": self._y,
            "id_bridge": self._id_bridge
        })
        return dict

    @property
    def pods(self):
        return self._pods_previous + self._pods_next + self._pods_beside
