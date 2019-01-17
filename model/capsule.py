#! /usr/bin/env python3
# coding: utf-8

capsule_id = 0


class Capsule:
    # capsule data
    is_moving = False
    is_loaded = False
    current_station = None
    final_destination = None
    # network data
    network_map = None
    network = None

    def __init__(self, name=None, station=None):
        global capsule_id
        self.id = capsule_id
        capsule_id += 1
        self.name = "Capsule #{0}".format(self.id) if (name is None) else name
        if station != None:
            self.depart_station = station
            self.next_switch = station.next_switch

    def _ask_route(self, switch):
        change = switch.route_capsule_to_station(self, self.final_destination)
        if change:
            self._change_loop(switch)
        else:
            self._do_a_loop(switch.next_station)

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

    def _change_loop(self, switch):
        # TODO

        return

    def _do_a_loop(self, station):
        # TODO
        return

    def _refresh_map(self):
        # TODO
        return

    def show_details(self, station):
        # TODO
        return
