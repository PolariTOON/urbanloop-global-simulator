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
        pods = []
        for pod_index in range(len(section.pods)):
            pod = section.pods[pod_index]
            pod = pod.serialize()
            pod.update({
                "x": 0,  # TODO
                "y": 0  # TODO
            })
            pods.append(pod)
        section = section.serialize()
        dict = super().serialize()
        dict.update({
            "section": section,
            "pods": pods
        })
        return dict

    @property
    def pods(self):
        return [pod for route in self._routes for pod in route.pods]
