"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""

from ...node2 import Node


class Way(Node):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
