"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""

from ...node2 import Node


class Way(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def serialize(self):
        return super().serialize().update({})
