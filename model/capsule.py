#! /usr/bin/env python3
# coding: utf-8
from model.switch import Switch

capsule_id = 0  # type: int


class Capsule:

    def __init__(self, station=None, destination=None):
        """
        initialisation d'une capsule
            :param  station : Station où la capsule est initiee (Station)
            :return: 0UT : un objet Capsule (Capsule)
        """
        global capsule_id
        self.id = capsule_id
        capsule_id += 1
        # self.name = "Capsule #{0}".format(self.id) if (name is None) else name
        self.current_element = None
        self.next_element = None
        if station is not None:
            self.current_element = station
            self.next_element = station.next_element
            self.loop = station.loop
        self.destination = destination

    def ask_route(self, switch):
        """
        Demande au switch de calculer sa route : va déclencher le changement ou non de boucle
            :param  switch : Switch "suivant" a qui la capsule demande d'etre routé (Switch) OBLIGATOIRE
            :return: void : mise à jour
        """
        change = switch.route_capsule_to_station(self.destination)
        if change:
            self._change_loop(switch)
        else:
            self._continue_on_loop(switch)

    def _change_loop(self, switch):
        """
        Lorsque l'aiguillage indique qu'il faut changer de boucle
            :param switch: l'aiguillage qui a dit qu'il fallait changer de boucle
            :return: void : change "l'élément suivant
        """
        self.current_element = switch.next_element_other
        self.loop = switch.other_loop
        d, self.next_element = self.loop.dist_to_next_object(self.current_element)
        return

    def _continue_on_loop(self, element):
        """
         Lorsque qu'il faut rester sur la boucle (la station n'est pas la destination ou pas accessible ou le switch ne veut pas aiguiller
            :param element: l'element qui fait qu'on doit rester sur la boucle
            :return: void
        """
        self.current_element = element.next_element
        self.next_element = self.loop.dist_to_next_object(self.current_element)
        return

# TODO nettoyage
    ''' 
    def _start_moving_to(self, station):
        # TODO
        return

    def _enter_into(self, station):
        # TODO
        return

    def _has_arrived_to(self, station):
        # TODO
        return

    def _prepare_leaving(self, station):
        # TODO
        return

    def _leave(self, station):
        # TODO
        return

    def _insertion_into_loop(self):
        # TODO
        return
    def _refresh_map(self):
        # TODO
        return

    def show_details(self, station):
        # TODO
        return'''
