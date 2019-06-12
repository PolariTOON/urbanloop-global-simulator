"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""


class RouteNode:

    angle = 0

    def __init__(self, angle=0):
        self.capsules = []
        self.angle = angle
