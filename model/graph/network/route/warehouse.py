"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des capsules
"""

from .route_node import RouteNode


class Warehouse(RouteNode):
    def __init__(self):
        pass

    def serialize():
        return super.serialize().update({
            'jsonType': 'station'
        })
