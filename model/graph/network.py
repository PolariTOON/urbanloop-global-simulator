"""
Cette classe gère un réseau entier, c'est le niveau meta-graph du réseau
les noeuds peuvent être des routes (partie interne d'une boucle) ou des ponts (pour relier les boucles)
"""


class Network:

    nodes = None
    arcs = None


    def __init__(self, json_network):
        self.nodes = []
        self.arc = []
