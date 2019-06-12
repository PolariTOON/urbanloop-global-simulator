"""
2eme possibilité de noeud
Une route est à la fois un noeud du meta-graphe et un sous-graphe divisé en sections, stations, garages séparés par des capteurs
"""

from network_node import NetworkNode


class Route(NetworkNode):

    nodes = None
    arcs = None

    def __init__(self):
        self.nodes = []
        self.arc = []
