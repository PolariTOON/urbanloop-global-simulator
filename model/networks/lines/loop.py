"""
Réunis des routes pour former les boucles du réseau
"""

from .line import Line
from math import inf


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
    def x_min(self):
        return self.min_xy(True)

    @property
    def x_max(self):
        return self.max_xy(True)

    @property
    def y_min(self):
        return self.min_xy(False)

    @property
    def y_max(self):
        return self.max_xy(False)

    @property
    def length(self):
        d = 0
        for r in self._routes:
            d += r.length
        return d

    def min_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus petite abscisse ou ordonnée selon le choix, parmi les éléments de la boucle
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        mini = inf
        for index in range(len(self._routes)):
            if choice:
                temp = self._routes[index].x_min
            else:
                temp = self._routes[index].y_min
            if temp < mini:
                mini = temp
            if choice:
                temp = self._switches[index].x
            else:
                temp = self._switches[index].y
            if temp < mini:
                mini = temp
        return mini

    def max_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus grande abscisse ou ordonnée selon le choix, parmi les éléments de la boucle
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        maxi = 0
        for index in range(len(self._routes)):
            if choice:
                temp = self._routes[index].x_max
            else:
                temp = self._routes[index].y_max
            if temp > maxi:
                maxi = temp
            if choice:
                temp = self._switches[index].x
            else:
                temp = self._switches[index].y
            if temp < maxi:
                maxi = temp
        return maxi

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

    def distance_between_steps(self, step1, step2):
        distance = None
        for route in self._routes:
            for step in route.steps:
                if step == step1:
                    distance = 0
                if distance is not None and step == step2:
                    return distance
                if distance is not None:
                    distance += step.next.length
        return distance
