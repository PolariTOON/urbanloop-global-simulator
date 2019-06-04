from model import identifier

all_sensors = {}


class Sensor:
    def __init__(self, angle=-1, capsule=None, loop=None):
        self.id = identifier.generate_sensor_id()
        self.angle = angle
        self.capsule = capsule
        self.loop = loop
        self.section_loop = None
        self.name = 'sensor n°%d' % self.id
        self.uuid = identifier.generate_unique()


def get_sensors():
    return all_sensors
