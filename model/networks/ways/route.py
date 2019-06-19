"""
2eme possibilité de noeud
Une route est à la fois un noeud du graphe subdivisé et un graphe divisé en sections, stations, garages séparés par des capteurs
"""
from model.networks.roads.tracks.sensor import Sensor
from model.networks.roads.tracks.station import Station
from model.networks.roads.tracks.warehouse import Shed
from .way import Way


class Route(Way):
    def __init__(self, id, steps):
        super().__init__()
        self.id = id
        self._sections = []
        self._steps = []  # liste contenant des warehouses, stations et capteurs au format json
        self.build(steps)

    @property
    def capsules(self):
        return [capsule for section in self.sections for capsule in section.capsules] + [capsule for step in self.steps
                                                                                         for capsule in step.capsules]

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

    def build(self, steps):
        #  TODO : contruction de la route à partir des tracks la composant

        for step in range(len(steps)):
            if step["type"] == "station":
                new_station = Station(step["name"], step["capacity"], step["capsule_count"], step["station_type"], step["x"], step["y"])
                self._steps.append(new_station)
            elif step["type"] == "warehouse":
                new_warehouse = Shed(step["name"], step["capacity"], step["capsule_count"], step["x"], step["y"])
                self._steps.append(new_warehouse)
            elif step["type"] == "sensor":
                new_sensor = Sensor(step["x"], step["y"])
                self._steps.append(new_sensor)
            else:
                print("ERROR TYPE OF STEP")
