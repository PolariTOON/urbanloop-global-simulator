"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""
from ...node import Node


class Way(Node):
    def __init__(self, env, id, pod_size, **kwargs):
        super().__init__(env, id, **kwargs)
        self._parent = None
        self._pod_size = pod_size

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def pod_size(self):
        return self._pod_size
