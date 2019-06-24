"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from .line import Line


class Bridge(Line):
    def __init__(self, id, routes=None, switches=None, **kwargs):
        super().__init__(id, **kwargs)
        self._routes = routes or []
        self._switches = switches or []

    def serialize(self):
        section = self._routes[0].sections[0]
        dict = super().serialize()
        dict.update({
            "section": section.serialize(),
            "pods": [pod.serialize() for pod in section.pods]
        })
        return dict

    @property
    def pods(self):
        pods = []
        for route in self._routes:
            for section in route.sections:
                for pod in section.pods:
                    pods.append(pod)
        return pods