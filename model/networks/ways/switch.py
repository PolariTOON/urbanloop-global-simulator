from ..tokens.pod import Pod
from .way import Way


class Switch(Way):
    def __init__(self, env, id, margin_min, pod_size, max_speed, x=None, y=None, previous=None, next=None, beside=None, pods=None, id_bridge=None, **kwargs):
        super().__init__(env, id, pod_size, **kwargs)
        self._x = x or 0
        self._y = y or 0
        self._previous = previous
        self._next = next
        self._beside = beside
        self._pods = pods or []
        self._id_bridge = id_bridge
        self._rules = []
        self._margin = self.speed * (margin_min + pod_size) / 8.33 - pod_size
        self._max_speed = max_speed

        # Ajout des capsules
        for pod in pods:
            speed = pod["speed"]
            self._pods.append(Pod(env, self, speed, **pod))

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
    def margin(self):
        return self._margin

    @property
    def place_size(self):
        return self.pod_size + self.margin

    @property
    def beside(self):
        return self._beside

    @property
    def speed(self):
        return self._next.sections[0].speed

    @property
    def max_speed(self):
        return self._max_speed  # en m/s

    @property
    def next(self):
        return self._next

    @property
    def previous(self):
        return self._previous

    @property
    def speed_loop(self):
        return self._previous.sections[-1].speed

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
