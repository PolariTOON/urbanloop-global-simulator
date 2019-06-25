import math

from model import identifier, station, switch, warehouse, sensor
from settings import simlog, network

all_loops = {}


class Loop:
    def __init__(self, name, size=100, coordinates=None):
        """
        initialisation d'une station
        :param name : Nom de la boucle /!\ fait office d'identifiant (String) OBLIGATOIRE
        :param size : Circonference de la boucle (float)
        :param coordinates : tableau des coordonees sous la forme [x,y] ([float, float])
        :return:0UT : un objet Loop (Loop)
        """
        self.uuid = identifier.generate_unique()
        self.id = identifier.generate_loop_id()
        self.name = name
        simlog.info("Create loop " + self.name)
        self.clockwise = True
        if coordinates is not None:
            self.x = coordinates[0]
            self.y = coordinates[1]
        self.size = size
        global all_loops
        all_loops[self.name] = self
        self.stations = []
        self.switches = []
        self.objects = []
        self.lengths = []
        self.sensors = []
        self.sensors_lengths = []  # distance au prochain capteur
        self.all_objects = []  # objects et sensors
        self.all_objects_lengths = []

    def add_order(self, order):
        """
         permet d'ajouter les elements dans la boucle en déterminant leur position
         (objects de la forme [nature, pointeur, angle])
            :param  order : tableau contenant le nécessaire pour cette mise à jour
                                                                ([string, Switch/Station, float]) OBLIGATOIRE
            :return: void (mise à jour de objects et lengths)
        """
        self.objects = []
        self.lengths = [0 for i in order]
        for i in range(len(order)):
            element = order[i]
            # mise à jour des suivants + object[i] = [nature, obj, angle]
            # On prend le reste car c'est une boucle donc le suivant du dernier est le premier
            if type(element) is switch.Switch and element.other_loop == self:  # switch_in
                element.next_element_other = order[(i + 1) % len(order)]
                self.objects += [["switch_in", element, element.angle_other_loop]]
                self.switches += [element]
            else:
                element.next_element = order[(i + 1) % len(order)]
                if type(element) is switch.Switch:  # switch_out
                    self.objects += [["switch_out", element, element.angle_my_loop]]
                    self.switches += [element]
                elif type(element) is station.Station:
                    self.objects += [["station", element, element.angle]]
                    self.stations += [element]
                elif type(element) is warehouse.Warehouse:
                    self.objects += [["warehouse", element, element.angle]]

        # mise à jour des longueurs
        nb_elements = len(self.objects)
        for i in range(nb_elements):
            an_object = self.objects[i]
            next_object = self.objects[(i + 1) % nb_elements]
            if self.clockwise:  # sens horaire des angles
                angle_next = an_object[2] - next_object[2]
            else:  # sens trigonométrique des angles
                angle_next = next_object[2] - an_object[2]
            angle_next = angle_next % 360
            self.lengths[i] = round(float(angle_next / 360) * self.size,
                                    2)  # arc = D*pi*angle/360  et D = circonference/pi
            if self.size is None:
                self.size = sum(self.lengths)

    def distance_between(self, element1, element2):
        for i in range(len(self.objects)):
            element = self.objects[i][1]
            if element is element1:
                if element is element2:  # on veut la taille du switch element1
                    return element.size
                distance = 0
                for j in range(i + 1, len(self.objects) + i + 1):
                    index = j % len(self.objects)
                    element = self.objects[index][1]
                    distance += self.lengths[index - 1]
                    if element is element2:
                        return distance
        return None

    def get_index_of(self, an_object):
        for i in range(len(self.objects)):
            if self.objects[i][1] is an_object:
                return i
        return None

    def add_sensors(self, sensors):
        """
        Permet d'ajouter les sensors dans la boucle sans qu'ils interfèrent avec les noeuds du graphe
        calcul aussi la position
        Initialise les next_sensor
        :param sensors: tableau contenant le nécessaire pour cette mise à jour ([string, Sensor, float]) OBLIGATOIRE
        :return: void (mise à jour des capteurs et de sensor_lengths)
        """
        self.sensors = sensors
        self.sensors_lengths = [0 for s in sensors]
        nb_sensor = len(self.sensors)
        for i in range(nb_sensor):
            a_sensor = self.sensors[i]
            next_sensor = self.sensors[(i + 1) % nb_sensor]
            a_sensor.next_sensor = next_sensor
            if self.clockwise:
                next_angle = a_sensor.angle - next_sensor.angle
            else:
                next_angle = next_sensor.angle - a_sensor.angle
            next_angle = next_angle % 360
            self.sensors_lengths[i] = round(float(next_angle / 360) * self.size, 2)
            if self.size is None:
                self.size = sum(self.sensors_lengths)

    def get_angle_in_loop(self, elm):
        if type(elm) is not switch.Switch:
            return elm.angle
        elif elm.my_loop is self:
            return elm.angle_my_loop
        else:
            return elm.angle_other_loop

    def init_all_objects(self):
        """
        Initialise les tableaux annexes all_objects et all_objects_lengths qui contiennent
        respectivement tous les objets dans la boucle (garage, station, switch, capteur)
        et les distances d'un objet au suivant
        Un objet est de la forme : ["type", objet, angle]
        :return: (void) Les éléments all_objects et all_objects_lengths sont remplis
        """
        for o in self.sensors:
            self.all_objects += [['sensor', o, float(o.angle)]]
        for o in self.objects:
            self.all_objects.append(o)
        self.all_objects.sort(key=lambda obj: obj[2])
        self.all_objects_lengths = [0 for o in self.all_objects]
        nb_objects = len(self.all_objects)
        for i in range(nb_objects):
            a_object = self.all_objects[i]
            next_object = self.all_objects[(i + 1) % nb_objects]
            a_angle = a_object[2]
            next_obj_angle = next_object[2]
            if self.clockwise:
                next_angle = a_angle - next_obj_angle
            else:
                next_angle = next_obj_angle - a_angle
            next_angle = next_angle % 360
            self.all_objects_lengths[i] = round(float(next_angle / 360) * self.size, 2)
            if self.size is None:
                self.size = sum(self.sensors_lengths)

    def get_radius(self):
        return self.size / (2 * math.pi)

    def serialize(self):
        return {
            'uuid': str(self.uuid),
            'id': self.id,
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'radius': math.floor(self.size / (2 * math.pi)),
            'size': self.size,
            'clockwise': self.clockwise
        }

def get_by_name(search_name):
    """
    cette fonction indépendante d'une boucle permet de récupérer un objet station en ne connaissant que son nom
        :param  search_name : le nom de la boucle cherchée (String) OBLIGATOIRE
        :return: la Loop (si elle existe) ayant le nom voulu (Loop)
    """
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    print("La boucle recherchée n'existe pas")
    return None


def get_loops():
    return [loop for _, loop in all_loops.items()]
