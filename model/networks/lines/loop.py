"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, routes=None, switches=None, **kwargs):
        super().__init__(**kwargs)
        self._routes = routes
        self._switches = switches

    @property
    def routes(self):
        return self._routes

    @property
    def pods(self):
        return [p for p in self.routes.pods]

    def serialize(self):
        elements = []
        sections = []
        pods = []
        for e in range(len(self._switches)):
            elements.append(self._switches[e].serialize())
            for step in range(len(self._routes[e].steps)):
                elements.append(self._routes[e].steps[step].serialize())
                sections.append(self._routes[e].sections[step].serialize())
                for pod in range(self._routes[e].sections[step].pods):
                    pods.append(self._routes[e].sections[step].pods[pod].serialize())
        return super().serialize().update({
            "name": self._name,
            "elements": elements,
            "sections": sections,
            "pods": pods
        })

