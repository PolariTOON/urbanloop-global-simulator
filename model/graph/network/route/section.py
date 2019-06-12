"""
Possibilité de noeud du sous-graphe désignant une section de route
"""
from model.graph.network.route.route_node import RouteNode


class Section(RouteNode):
    def __init__(self, len):
        super().__init__()
        self.len = len  # taille de la section

    def serialize(self):
        return {
            'jsonType': 'section',
            'width': self.len
        }

    def get_len(self):
        return self.len
