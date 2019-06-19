"""
2eme possibilité de noeud
Une route est à la fois un noeud du graphe subdivisé et un graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .way import Way
from .tracks.sensor import Sensor
from .tracks.shed import Shed
from .tracks.station import Station


class Route(Way):
    def __init__(self, id, steps=None, sections=None, **kwargs):
        super().__init__(**kwargs)
        self.id = id
        self._steps = steps or []  # liste contenant des sheds, stations et capteurs au format json
        self._sections = sections or []
        self._init_route()  # steps_paths = [{"steps": [shed, capteur, station, ...], "paths": [{"type": machin}]}]
        self._previous_switch = None
        self._next_switch = None

    @property
    def pods(self):
        return [pod for section in self.sections for pod in section.pods] + [pod for step in self.steps for pod in step.pods]

    @property
    def sections(self):
        return self._sections

    @property
    def steps(self):
        return self._steps

    def serialize(self):
        return super().serialize().update({
            'type': 'route',
            'pod': ''  # TODO
        })

    def _init_route(self):
        #  TODO : contruction de la route à partir des tracks la composant

        for k in range(len(self._steps)):
            step = self._steps[k]
            if step["type"] == "sensor":
                self._steps[k] = Sensor(**step)
            elif step["type"] == "shed":
                self._steps[k] = Shed(**step)
            elif step["type"] == "station":
                self._steps[k] = Station(**step)
            else:
                print("ERROR TYPE OF STEP")
