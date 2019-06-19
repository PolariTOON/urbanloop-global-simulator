"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, routes=None, switches=None, name=None, paths=None, pods=None):
        super().__init__()
        self._routes = routes
        self._switches = switches
        self._name = name
        self._paths = paths
        self.init_pods(pods)

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

    """
    def init_pods(self, pods):
        for pod in pods:
            d = 0
            ok = False
            for route in self.routes:
                for section in route.sections:
                    d += section.len
                    if d > pod["position"]:
                        source =
                        section.add_pod(pod, source, destination, travelers)
                        ok = True
                        break
                if ok:
                    break
    """