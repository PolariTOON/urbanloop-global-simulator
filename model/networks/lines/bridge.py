"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""

from .line import Line


class Bridge(Line):
    def __init__(self, id, routes=None, switches=None, switch_out=None, switch_in=None, **kwargs):
        """
        Instancie un pont
        :param id: id du pont
        :param routes: liste des routes du pont (il n'y en a qu'une normalement)
        :param switches: liste des aiguillages du pont (il y en a 2 normalement)
        :param kwargs: dictionnaire comportant les informations du json
        """
        super().__init__(id, **kwargs)
        self._routes = routes or []
        self._switches = switches or []
        self._switch_out = switch_out or None
        self._switch_in = switch_in or None

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
            "name": self.name,
            "section": section,
            "pods": pods,
            "switch_in": self._switch_in,
            "switch_out": self._switch_out
        })
        return dict
