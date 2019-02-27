#! /usr/bin/env python3
# coding: utf-8
from settings import simlog

all_loops = {}
default_size = 100


class Loop:
    def __init__(self, name, size=default_size, coordinates=None):
        """
        initialisation d'une loop
        :param name : Nom de la boucle /!\ fait office d'identifiant (String) OBLIGATOIRE
        :param size : Circonference de la boucle (float)
        :param coordinates : tableau des coordonees sous la forme [x,y] ([float, float])
        :return:0UT : un objet Loop (Loop)
        """
        self.name = name
        simlog.info("Create loop " + self.name)
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

    def add_order(self, order):
        """
         permet d'ajouter les elements dans la boucle en déterminant leur position
         (objects de la forme [nature, pointeur, angle])
            :param  order : tableau contenant le nécessaire pour cette mise à jour
                                                                ([string, Switch/Station, float]) OBLIGATOIRE
            :return: void (mise à jour de objects et lengths)
        """
        self.objects = []
        self.lengths = []
        for i in range(len(order)):
            element = order[i]
            # order[i] = [nature, obj, angle]
            self.objects += [order[i]]
            # print(order[i])
            angle_next = order[(i + 1) % len(order)][2] - element[2]
            if angle_next < 0:
                angle_next += 360
            self.lengths += [float(angle_next / 360) * self.size]  # arc = 2*D*pi*angle/360  et D = circonference/pi
            if self.size is None:
                self.size = sum(self.lengths)

    def dist_to_next_object(self, element, element2=None):
        """
        determine la distance entre l'element et le second element ou bien le suivant (et dans ce cas on le retourne
        :param  element : element permettant de calculer "le suivant" (Station) OBLIGATOIRE
        :param  element2 : distance entre les 2 elements (Station) OBLIGATOIRE
        :return:0UT 1 : la distance à parcourir jusqu'au prochain objet sur la boucle (int)
                OUT 2 : le prochain objet sur la boucle (Station/Switch)
        """
        for i in range(len(self.objects)):
            if self.objects[i][1] == element:
                if element2 is None:
                    return self.lengths[i], self.objects[(i + 1) % len(self.objects)][1]
                else:
                    if element is element2:
                        # On veut la distance d'un switch in vers le même switch out
                        return element.size, element
                    cost = self.lengths[i]
                    for j in range(0, len(self.objects)):
                        index = (i + j) % len(self.objects)
                        cost += self.lengths[index]
                        if self.objects[index][1] is element2:
                            return cost, self.objects[index][1]
        return 0, None

    def show_details(self):
        """
        crée un text contenant toutes les informations à propos de la boucle
        :return: String
        """
        details = "Loop Name : " + self.name
        details += "\nCircumference : " + str(self.size)
        details += "\nCenter coordinates : x = " + str(self.x) + " ; y = " + str(self.y)
        details += "\nElements : "
        for o in self.objects:
            if o[0] == "station":
                details += "\n \t Station " + o[1].name
            else:
                details += "\n \t Switch "
                if o[0] == "switch_out":
                    details += "out " + str(o[1].id) + " to " + o[1].other_loop.name
                else:
                    details += "in " + str(o[1].id) + " from " + o[1].my_loop.name
        return details


def get_by_name(search_name):
    """
    cette fonction indépendante d'une boucle permet de récupérer un objet loop en ne connaissant que son nom
        :param  search_name : le nom de la boucle cherchée (String) OBLIGATOIRE
        :return: 0UT : la Loop (si elle existe) ayant le nom voulu (Loop)
    """
    for name, loop in all_loops.items():
        if name == search_name:
            return loop
    return None


def get_loops():
    return [loop for _, loop in all_loops.items()]
