"""
2eme possibilité de noeud
Une route est à la fois un noeud du graphe subdivisé et un graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .way import Way
from .tracks.section import Section
from .tracks.sensor import Sensor
from .tracks.shed import Shed
from .tracks.station import Station


class Route(Way):
    def __init__(self, id, steps=None, sections=None, **kwargs):
        super().__init__(id, **kwargs)
        self._steps = steps or []  # [shed, capteur, station, ...]
        self._sections = sections or []  # [{"type": "machin"}, ...](le bon nombre = 1 de + que de steps)
        self._previous = None
        self._next = None

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
    def pods(self):
        return [pod for section in self.sections for pod in section.pods] + [pod for step in self.steps for pod in step.pods]

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "route",
            "pod": self.pods
        })
        return dict
