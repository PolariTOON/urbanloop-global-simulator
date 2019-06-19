"""
Classe abstraite représentant les noeuds des sous-graphes du réseau
"""

from .track import Track


class Step(Track):
    def __init__(self):
        super().__init__()

    def serialize(self):
        return super().serialize().update({})
