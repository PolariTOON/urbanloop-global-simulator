"""
Réunis des routes pour former les boucles du réseau
"""

from . import Line


class Loop(Line):
    def __init__(self):
        super().__init__(self)
        self._routes = []

    def serialize():
        return super().serialize().update({})
