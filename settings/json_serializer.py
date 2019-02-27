import math


def serialize_loop(loop):
    return {
        'id': 1,  # TODO change name by id
        'name': loop.name,
        'radius': math.floor(loop.size / (2 * math.pi)),
        'x': loop.x,
        'y': loop.y
    }


def serialize_station_set_data(station):
    return {
        'id': 1,
        'name': station.name,
        'loop': station.loop.name,  # TODO Change name by a real id
        'angle': station.angle,
        'capacity': station.capacity
    }


def serialize_station_var_data(station):
    return {
    }


def serialize_switch_set_data(switch):
    return {
        'id': 1,
        'loopIn': switch.my_loop.name,  # TODO Change name by a real id
        'loopOut': switch.other_loop.name,
        'angleLoopIn': switch.angle_my_loop,
        'angleLoopOut': switch.angle_other_loop
    }


def serialize_switch_var_data(switch):
    return {
    }


def serialize_capsule(capsule):
    return {
    }
