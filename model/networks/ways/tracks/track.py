"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from ....node2 import Node


class Track(Node):
    def __init__(self, previous_track, next_track, **kwargs):
        super().__init__(**kwargs)
        self._previous_track = previous_track
        self._next_track = next_track
        self._pods = []

    @property
    def pods(self):
        return self._pods

    @property
    def previous_track(self):
        return self._previous_track

    @previous_track.setter
    def previous_track(self, value):
        self._previous_track = value

    @property
    def next_track(self):
        return self._next_track

    @next_track.setter
    def next_track(self, value):
        self._next_track = value

    def serialize(self):
        return super().serialize().update({})
