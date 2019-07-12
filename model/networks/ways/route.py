"""
2eme possibilité de noeud
Une route est à la fois un noeud du graphe subdivisé et un graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .way import Way
from .tracks.section import Section
from .tracks.sensor import Sensor
from .tracks.shed import Shed
from .tracks.station import Station
import math


class Route(Way):
    def __init__(self, id, steps=None, sections=None, **kwargs):
        super().__init__(id, **kwargs)
        self._steps = steps or []  # [shed, capteur, station, ...]
        self._sections = sections or []  # [{"type": "machin"}, ...](le bon nombre = 1 de + que de steps)
        self._previous = None
        self._next = None
        self._weight = 0

        #  Etape 42 : On instancie les pistes mais pas les liaisons de la premiere et de la dernière section
        for section_index in range(len(self._sections)):
            section = self._sections[section_index]
            section = Section(section_index, **section)
            self._sections[section_index] = section
        for step_index in range(len(self._steps)):
            step = self._steps[step_index]
            step["previous"] = self._sections[step_index]
            step["next"] = self._sections[step_index + 1]
            if step["type"] == "sensor":
                step = Sensor(step_index, **step)
            elif step["type"] == "shed":
                step = Shed(step_index, **step)
            elif step["type"] == "station":
                step = Station(step_index, **step)
            else:
                raise TypeError("invalid element type")
            self._steps[step_index] = step

    @property
    def sections(self):
        return self._sections

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

    @property
    def steps(self):
        return self._steps

    @property
    def sensors(self):
        return [step for step in self._steps if isinstance(step, Sensor)]

    @property
    def sheds(self):
        return [step for step in self._steps if isinstance(step, Shed)]

    @property
    def stations(self):
        return [step for step in self._steps if isinstance(step, Station)]

    @property
    def pods(self):
        return [pod for track in self._sections + self._steps for pod in track.pods]

    @property
    def length(self):
        length = 0
        for section in self._sections:
            length += section.length
        return length

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def expected_weight(self):
        """Poids de la route ne dépendant pas de la congestion"""
        weight = 0
        for section in self._sections:
            weight += section.weight
        return weight

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

    def min_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus petite abscisse ou ordonnée selon le choix, parmi les éléments de la route
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        mini = math.inf
        for step in self._steps:
            if choice:
                temp = step.x
            else:
                temp = step.y
            if temp < mini:
                mini = temp
        return mini

    def max_xy(self, choice):
        """
        :param choice: si True alors on travaille avec x (abscisse) sinon on travaille en y (ordonnée)
        :return: (float) la plus grande abscisse ou ordonnée selon le choix, parmi les éléments de la route
        (utile pour récupérer les dimensions du réseau dans la vue)
        """
        maxi = 0
        for step in self._steps:
            if choice:
                temp = step.x
            else:
                temp = step.y
            if temp > maxi:
                maxi = temp
        return maxi

    def serialize(self):
        pods = [pod.serialize() for track in self._sections + self._steps for pod in track.pods]
        dict = super().serialize()
        dict.update({
            "pod": pods
        })
        return dict
