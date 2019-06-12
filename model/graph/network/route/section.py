"""
Possibilité de noeud du sous-graphe désignant une section de route
"""

from .route_node import RouteNode


class Section(RouteNode):
    def __init__(self, len):
        self.len = len  # taille de la section

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'section',
            'len': self.len
        })
