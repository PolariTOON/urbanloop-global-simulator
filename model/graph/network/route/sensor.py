"""
C'est la représentation des arcs du sous-graphe du réseau
Cela permet 'avoir un capteur entre chaque section, tout comme dans un réseau réel idéal
"""
from model.graph.network.route.route_arc import RouteArc


class Sensor(RouteArc):
    def __init__(self, next_node, previous_node):
        super().__init__()
        self.next_node = next_node
        self.previous_node = previous_node

    def get_next_node(self):
        return self.next_node

    def get_previous_node(self):
        return self.previous_node

    def serialize(self):
        return {
            'jsonType': 'sensor',
            'next_node': self.next_node,
            'previous_node': self.previous_node
        }
