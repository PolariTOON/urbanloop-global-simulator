from math import pi


def serialize_loop(loop):
    return {
        'id': 1,  # TODO change name by id
        'name': loop.name,
        'radius': round(loop.size / (2 * pi)),
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
    }


def serialize_switch_var_data(switch):
    return {
    }


def serialize_capsule(capsule):
    return {
    }
