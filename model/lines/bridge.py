"""
1ere possibilité de noeud
Représentation de la portion de voie entre deux boucles (la voie qui est entre deux switchs de boucles différentes)
"""
from .line import Line


class Bridge(Line):
    def __init__(self, id, roads=None, switch_out=None, switch_in=None, **kwargs):
        """
        Instancie un pont
        :param id: id du pont
        :param roads: liste des routes du pont (il n'y en a qu'une normalement, mais on pourrait imaginer avoir un autre bridge sur celui-ci)
        :param kwargs: dictionnaire comportant les informations du json
        """
        super().__init__(id, **kwargs)
        self._roads = roads or []
        self._switch_out = switch_out or None
        self._switch_in = switch_in or None

    def serialize(self):
        road = self._roads[0] # on suppose qu'il n'y a qu'une route, tant qu'il n'y a aucun moyen de lier les routes entre elles (par ex avec des switchs)
        sections = []
        elements = []
        pods = []
        length = 0
        for section in road.sections:
            for pod_index in range(len(section.pods)):
                pod = section.pods[pod_index]
                pod = pod.serialize()
                pod.update({
                    "position": length + pod["position"] # position dans le bridge = longueur des précédentes sections + position dans la section actuelle
                })
                pods.append(pod)
            length += section.length
            sections.append(section.serialize())
        for step in road.steps:
            elements.append(step.serialize())
        dict = super().serialize()
        dict.update({
            "elements": elements,
            "sections": sections,
            "pods": pods,
            "switch_out": self.switch_out,
            "switch_in": self.switch_in
        })
        return dict

    @property
    def name(self):
        return super().name or "Bridge %d" % self.id

    @property
    def switch_out(self):
        return self._switch_out

    @property
    def switch_in(self):
        return self._switch_in
