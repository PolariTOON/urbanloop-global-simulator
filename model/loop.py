from model import identifier, station, switch
from settings import simlog

all_loops = {}
default_size = 100


class Loop:
    def __init__(self, name, size=default_size, coordinates=None):
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
            if type(element) is switch.Switch and element.other_loop == self:  # switch_in
                element.next_element_other = order[(i + 1) % len(order)]
                self.objects += [["switch_in", element, element.angle_other_loop]]
                self.switches += [element]
            else:
                element.next_element = order[(i + 1) % len(order)]
                if type(element) is switch.Switch:  # switch_out
                    # element.previous_element = order[(i - 1) % len(order)]
                    self.objects += [["switch_out", element, element.angle_my_loop]]
                    self.switches += [element]
                elif type(element) is station.Station:
                    self.objects += [["station", element, element.angle]]
                    self.stations += [element]
                else:
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
            if angle_next < 0:
                angle_next += 360
            # print(an_object[1].name, next_object[1].name, angle_next)
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


def get_by_name(search_name):
    """
    cette fonction indépendante d'une boucle permet de récupérer un objet station en ne connaissant que son nom
        :param  search_name : le nom de la boucle cherchée (String) OBLIGATOIRE
        :return: 0UT : la Loop (si elle existe) ayant le nom voulu (Loop)
    """
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    return None


def get_loops():
    return [loop for _, loop in all_loops.items()]
