"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, routes=None, switches=None, **kwargs):
        super().__init__()
        self._routes = routes
        self._switches = switches

    @property
    def routes(self):
        return self._routes

    @property
    def pods(self):
        return [p for p in self.routes.pods]

    def serialize(self):
        return super().serialize().update({
            "type": "loop",
            "name": self._name,
            "paths": self._paths
        })

