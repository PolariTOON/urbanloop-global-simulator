"""
Possibilité de noeud du sous-graphe désignant une section de route
"""

from math import hypot, nan
from ...tokens.pod import Pod
from .track import Track


class Section(Track):
    def __init__(self, speed=None, path=None, **kwargs):
        super().__init__(**kwargs)
        speed = speed or 0
        path = path or {
            "type": "line"
        }
        path["type"] = path["type"] or "line"
        self._speed = speed
        self._path_type = path["type"]
        self._length = nan
        self._previous = None
        self._next = None

    @property
    def speed(self):
        return self._speed

    @property
    def length(self):
        return self._length

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value
        other = self._next
        if value is None or other is None:
            self._length = nan
        else:
            self._length = hypot(other.x - value.x, other.y - value.y) # TODO: gérer les autres types de chemins

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value
        other = self._previous
        if value is None or other is None:
            self._length = nan
        else:
            self._length = hypot(other.x - value.x, other.y - value.y) # TODO: gérer les autres types de chemins

    def serialize(self):
        return super().serialize().update({
            "speed": self._speed,
            "path": {
                "type": self._path_type
            }
        })

    def insert_pod(self, **pod):
        pods = self._pods
        for k in range(len(pods)):
            if pods[k].position > pod["position"]:
                pods.insert(k, Pod(**pod))
                return
        pods.append(Pod(**pod))
