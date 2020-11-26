"""
Réunis des routes pour former les boucles du réseau
"""
from math import inf

from .line import Line


class Loop(Line):
    def __init__(self, id, roads=None, switches=None, side_elements=None, **kwargs):
        """
        Instancie une boucle
        :param id: id de la boucle
        :param roads: liste des routes de la boucle
        :param switches: liste des aiguillages de la boucle
        :param side_elements: liste des stations et sheds de la boucle (ils ne sont pas dans la boucles mais sur ses dérivations)
        :param kwargs: dictionnaire comportant les informations du json
        """
        super().__init__(id, **kwargs)
        self._roads = roads
        self._switches = switches
        self._side_elements = side_elements

    @property
    def name(self):
        return super().name or "Loop %d" % self.id

    @property
    def roads(self):
        return self._roads

    @property
    def switches(self):
        return self._switches

    @property
    def side_elements(self):
        return self._side_elements

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
        for r in self._roads:
            d += r.length
        return d

    def get_element(i_element):

        return

    def min_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus petite abscisse ou ordonnée selon le choix, parmi les éléments de la boucle
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        mini = inf
        for index in range(len(self._roads)):
            if choice:
                temp = self._roads[index].x_min
            else:
                temp = self._roads[index].y_min
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
        for index in range(len(self._roads)):
            if choice:
                temp = self._roads[index].x_max
            else:
                temp = self._roads[index].y_max
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
        switches = self.switches
        roads = self.roads
        length = 0
        for way_index in range(len(switches)):
            switch = switches[way_index]
            switch = switch.serialize()
            elements.append(switch)
            road = roads[way_index]
            for step_index in range(len(road.steps)):
                step = road.steps[step_index]
                step = step.serialize()
                elements.append(step)
            for section_index in range(len(road.sections)):
                section = road.sections[section_index]
                for pod_index in range(len(section.pods)):
                    pod = section.pods[pod_index]
                    position = pod.position
                    position += length
                    pod = pod.serialize()
                    pod.update({
                        "position": position
                    })
                    pods.append(pod)
                length += section.length
                section = section.serialize()
                sections.append(section)
        # TODO : à faire autrement
        for e in self._side_elements:
            step = e.serialize()
            elements.append(step)
        #
        dict = super().serialize()
        dict.update({
            "elements": elements,
            "sections": sections,
            "pods": pods
        })
        return dict

    def distance_between_steps(self, step1, step2):
        distance = None
        for road in self._roads:
            for step in road.steps:
                if step == step1:
                    distance = 0
                if distance is not None and step == step2:
                    return distance
                if distance is not None:
                    distance += step.next.length
        return distance
