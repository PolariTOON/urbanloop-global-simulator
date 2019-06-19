"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""

from ...node2 import Node


class Way(Node):
    def __init__(self):
        super().__init__()

    def serialize(self):
        return super().serialize().update({})
