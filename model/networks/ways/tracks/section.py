"""
Possibilité de noeud du sous-graphe désignant une section de route
"""

from math import hypot, nan
from ...tokens.pod import Pod
from .track import Track


class Section(Track):
    def __init__(self, id, speed=None, path=None, **kwargs):
        super().__init__(id, **kwargs)
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
        self._pods = []

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
            self._length = hypot(other.x - value.x, other.y - value.y)  # TODO: gérer les autres types de chemins

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
            self._length = hypot(other.x - value.x, other.y - value.y)  # TODO: gérer les autres types de chemins

    @property
    def pods(self):
        return self._pods

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "speed": self._speed,
            "path": {
                "type": self._path_type
            }
        })
        return dict

    def insert_pod(self, pos_from_section, **pod):
        pods = self._pods
        for k in range(len(pods)):
            if pods[k].position > pos_from_section:
                self._pods.insert(k, Pod(**pod))
                return
        self._pods.append(Pod(**pod))
