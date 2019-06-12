"""
2eme possibilité de noeud
Une route est à la fois un noeud du meta-graphe et un sous-graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .network_node import NetworkNode


class Route(NetworkNode):
    def __init__(self):
        self._nodes = []
        self._arcs = []

    @property
    def capsules(self):
        return [capsule for node in self.nodes for capsule in node.capsules]

    @property
    def nodes(self):
        return self._nodes

    @property
    def arcs(self):
        return self._arcs

    def serialize(self):
        return super().serialize().update({
            'jsonType': 'route'
        })
