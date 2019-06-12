"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from network_node import NetworkNode


class Bridge(NetworkNode):

    def __init__(self):
        self.capsules = []
        pass
