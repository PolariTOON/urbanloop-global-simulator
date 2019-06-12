"""
Classe abstraite liée à un arc du meta-graphe représentant le réseau dans sa globalité
"""
from model.graph.arc import Arc


class NetworkArc(Arc):
    def __init__(self):
        pass

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'network_arc'
        })
