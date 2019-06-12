"""
Classe abstraite représentant les arcs des sous-graphes du réseau
"""
from model.graph.arc import Arc


class RouteArc(Arc):
    def __init__(self):
        pass

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'route_arc'
        })