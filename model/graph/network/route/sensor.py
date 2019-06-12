"""
C'est la représentation des arcs du sous-graphe du réseau
Cela permet 'avoir un capteur entre chaque section, tout comme dans un réseau réel idéal
"""
from model.graph.network.route.route_arc import RouteArc


class Sensor(RouteArc):
    def __init__(self, id_detected=-1):
        self.id_detected = id_detected

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'sensor'
        })
