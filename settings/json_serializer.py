from math import pi


def serialize_loop(loop):
    return {
        'id': 1,
        'name': loop.name,
        'radius': round(loop.size / (2 * pi)),
        'x': loop.x,
        'y': loop.y
    }


def serialize_station_set_data(station):
    return {
    }


def serialize_station_var_data(station):
    return {
    }


def serialize_switch_set_data(switch):
    return {
    }


def serialize_switch_var_data(switch):
    return {
    }


def serialize_capsule(capsule):
    return {
    }
