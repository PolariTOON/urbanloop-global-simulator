"""
Classe abstraite liée à un noeud du meta-graphe représentant le réseau dans sa globalité
"""

from ..node import Node


class NetworkNode(Node):
    def __init__(self):
        pass

    def serialize():
        return super().serialize().update({
            'jsonType': 'network_node'
        })
