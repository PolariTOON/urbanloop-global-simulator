from model import identifier

_sensors = list()


class Sensor:
    def __init__(self, angle=-1, capsule=None, loop=None):
        self.id = identifier.generate_sensor_id()
        self.angle = angle
        self.capsule = capsule
        self.loop = loop
        self.section_loop = None
        self.name = 'sensor n°%d' % self.id
        self.uuid = identifier.generate_unique()

    def serialize(self):
        return {
            'jsonType': 'sensor',
            'uuid': str(self.uuid),
            'id': self.id,
            'name': self.name,
            'capsule_id': self.capsule.id
        }


def get_sensors():
    return _sensors
