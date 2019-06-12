"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""


class Network:
    def __init__(self, json):
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
        return {
            'jsonType': 'network'
        }
