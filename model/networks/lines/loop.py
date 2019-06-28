"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line


class Loop(Line):
    def __init__(self, id, routes=None, switches=None, **kwargs):
        """
        Instancie une boucle
        :param id: id de la boucle
        :param routes: liste des routes de la boucle
        :param switches: liste des aiguillages de la boucle
        :param kwargs: dictionnaire comportant les informations du json
        """
        super().__init__(id, **kwargs)
        self._routes = routes
        self._switches = switches

    @property
    def routes(self):
        return self._routes

    @property
    def switches(self):
        return self._switches

    @property
    def pods(self):
        return [pod for route in self._routes for pod in route.pods]

    def serialize(self):
        elements = []
        sections = []
        pods = []
        switches = self._switches
        routes = self._routes
        length = 0
        for way_index in range(len(switches)):
            switch = switches[way_index]
            switch = switch.serialize()
            elements.append(switch)
            route = routes[way_index]
            for step_index in range(len(route.steps)):
                step = route.steps[step_index]
                step = step.serialize()
                elements.append(step)
            for section_index in range(len(route.sections)):
                section = route.sections[section_index]
                for pod_index in range(len(section.pods)):
                    pod = section.pods[pod_index]
                    position = pod.position
                    x, y = section.get_coordinates_of_position(position)
                    position += length
                    pod = pod.serialize()
                    pod.update({
                        "position": position,
                        "x": x,
                        "y": y
                    })
                    pods.append(pod)
                length += section.length
                section = section.serialize()
                sections.append(section)
        dict = super().serialize()
        dict.update({
            "elements": elements,
            "sections": sections,
            "pods": pods
        })
        return dict
