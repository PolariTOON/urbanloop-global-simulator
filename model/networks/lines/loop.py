"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, routes, switches, name, paths):
        super().__init__()
        self._routes = routes
        self._switches = switches
        self.name = name
        self.paths = paths

    def serialize(self):
        return super().serialize().update({
            "type": "loop",
            "name": self.name,
            "paths": self.paths
        })
