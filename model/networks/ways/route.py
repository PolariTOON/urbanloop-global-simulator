"""
2eme possibilité de noeud
Une route est à la fois un noeud du graphe subdivisé et un graphe divisé en sections, stations, garages séparés par des capteurs
"""
from model.networks.ways.tracks.section import Section
from .way import Way
from .tracks.sensor import Sensor
from .tracks.shed import Shed
from .tracks.station import Station


class Route(Way):
    def __init__(self, id, steps=None, sections=None, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self._steps = steps or []  # [shed, capteur, station, ...]
        self._sections = sections or []  # [{"type": "machin"}, ...](le bon nombre = 1 de + que de steps)
        self._previous_switch = None
        self._next_switch = None

        #  Etape 42 : On instancie les pistes mais pas les liaisons de la premiere et de la dernière section
        for s in range(len(self._steps)):
            self._sections[s] = Section(None, None, self._sections[s])
            if self._steps[s]["type"] == "station":
                self._steps[s] = Station(self._sections[s], None)
            elif self._steps[s]["type"] == "shed":
                self._steps[s] = Shed(self._sections[s], None)
            elif self._steps[s]["type"] == "sensor":
                self._steps[s] = Sensor(self._sections[s], None)
            else:
                raise TypeError("type ", self._steps[s]["type"], "is not a valid type for a step")
            self._sections[s].next_track = self._steps[s]
        self._sections.append(Section(self._steps[len(self._steps) - 1], None, self._sections[len(self._sections) - 1]))

    @property
    def pods(self):
        return [pod for section in self.sections for pod in section.pods] + [pod for step in self.steps for pod in
                                                                             step.pods]

    @property
    def sections(self):
        return self._sections

    @property
    def previous_switch(self):
        return self._previous_switch

    @previous_switch.setter
    def previous_switch(self, value):
        self._previous_switch = value

    @property
    def next_switch(self):
        return self._next_switch

    @next_switch.setter
    def next_switch(self, value):
        self._next_switch = value

    @property
    def steps(self):
        return self._steps

    def serialize(self):
        return super().serialize().update({
            'type': 'route',
            'pod': self.pods
        })

