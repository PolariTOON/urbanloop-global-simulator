"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, name, clockwise, paths):
        super().__init__()
        self._routes = []
        self._switches = []
        self.name = name
        self.clockwise = clockwise
        self.paths = paths

    def serialize(self):
        return super().serialize().update({
            "type": "loop"
        })
