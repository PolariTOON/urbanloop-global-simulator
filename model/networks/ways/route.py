"""
2eme possibilité de noeud
Une route est à la fois un noeud du graphe subdivisé et un graphe divisé en sections, stations, garages séparés par des capteurs
"""

from .way import Way
from .tracks.sensor import Sensor
from .tracks.station import Station
from .tracks.shed import Shed


class Route(Way):
    def __init__(self, id, paths=None, steps=None):
        super().__init__()
        self.id = id
        self._sections = paths or []
        self._steps = steps or []  # liste contenant des sheds, stations et capteurs au format json
        self._init_route()  # steps_paths = [{"steps": [shed, capteur, station, ...], "paths": [{"type": machin}]}]
        self._previous_switch = None
        self._next_switch = None

    @property
    def capsules(self):
        return [capsule for section in self.sections for capsule in section.capsules] + [capsule for step in self.steps for capsule in step.capsules]

    @property
    def sections(self):
        return self._sections

    @property
    def steps(self):
        return self._steps

    def serialize(self):
        return super().serialize().update({
            'type': 'route',
            'capsule': ''  # TODO
        })

    def _init_route(self):
        #  TODO : contruction de la route à partir des tracks la composant

        for k in range(len(self._steps)):
            step = self._steps[k]
            if step["type"] == "station":
                new_station = Station(step["name"], step["capacity"], step["capsule_count"], step["station_type"], step["x"], step["y"])
                self._steps[k] = new_station
            elif step["type"] == "shed":
                new_shed = Shed(step["name"], step["capacity"], step["capsule_count"], step["x"], step["y"])
                self._steps[k] = new_shed
            elif step["type"] == "sensor":
                new_sensor = Sensor(step["x"], step["y"])
                self._steps[k] = new_sensor
            else:
                print("ERROR TYPE OF STEP")
