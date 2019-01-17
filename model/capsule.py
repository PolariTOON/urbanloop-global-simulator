#! /usr/bin/env python3
# coding: utf-8

capsule_id = 0  # type: int


class Capsule:
    # capsule data
    is_moving = False
    is_loaded = False
    current_station = None
    final_destination = None
    # network data
    network_map = None
    network = None

    def __init__(self, station=None):
        """
        initialisation d'une capsule
            :param  station : Station où la capsule est initiee (Station)
            :return: 0UT : un objet Capsule (Capsule)
        """
        global capsule_id
        self.id = capsule_id
        capsule_id += 1
        # self.name = "Capsule #{0}".format(self.id) if (name is None) else name
        if station is not None:
            self.depart_station = station
            self.next_switch = station.next_switch

    def _ask_route(self, switch):
        """
        Demande au switch de calculer sa route : va déclencher le changement ou non de boucle
            :param  switch : Switch "suivant" a qui la capsule demande d'etre routé (Switch) OBLIGATOIRE
            :return: void
        """
        change = switch.route_capsule_to_station(self, self.final_destination)
        if change:
            self._change_loop(switch)
        else:
            self._do_a_loop(switch.next_station)

    def _change_loop(self, switch):
        # TODO specification + implementation

        return

    def _do_a_loop(self, station):
        # TODO specification + implementation
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
