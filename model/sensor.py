import math

from model import identifier, loop

_sensors = list()


class Sensor:
    def __init__(self, angle=-1, capsule=None, loop=None, next_sensor=None):
        _sensors.append(self)
        self.id = identifier.generate_sensor_id()
        self.angle = angle
        self.capsule = capsule
        self.loop = loop
        self.section_loop = None
        self.name = 'sensor n°%d' % self.id
        self.uuid = identifier.generate_unique()
        self.next_sensor = next_sensor

    def serialize(self):
        loop_radius = self.loop.get_radius()
        radius_angle = math.radians(self.angle)
        if self.capsule is not None:
            id_capsule = self.capsule.id
        else:
            id_capsule = -1

        return {
            'jsonType': 'sensor',
            'uuid': str(self.uuid),
            'id': self.id,
            'name': self.name,
            'capsule_id': id_capsule,
            'x': self.loop.x + loop_radius * math.cos(radius_angle),
            'y': self.loop.y + loop_radius * math.sin(radius_angle),
            'outerCircle': self.loop.name,
            'next_sensor': self.next_sensor.name
        }


def get_sensors():
    return _sensors


