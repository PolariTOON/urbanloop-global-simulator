#! /usr/bin/env python3
# coding: utf-8

capsule_id = 0


class Capsule:
    # capsule data
    is_moving = False
    is_loaded = False
    current_station = None
    next_switch = None
    final_destination = None
    velocity = 0
    acceleration = 0
    # parameters to inject
    security_distance = 5000  # millimeters
    release_time = 12345  # miilisec
    acceleration_time = 12345  # miilisec
    max_speed = 22.2  # m/s (80km/h)
    # network data
    network_map = None
    network = None

    def __init__(self, name, station):
        global capsule_id
        self.id = capsule_id
        capsule_id += 1
        self.name = "Capsule #{0}".format(self.id) if (name is None) else name
        self.current_station = station

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

    def _change_loop(self, station):
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
