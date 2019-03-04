import math

from model import switch


# CREATE OBJECT ID FOR ALL OBJECTS OF MODEL

def serialize_loop(loop):
    return {
        'id': loop.id,
        'name': loop.name,
        'x': loop.x,
        'y': loop.y,
        'radius': math.floor(loop.size / (2 * math.pi)),
        'size': loop.size,
        'objects': serialize_objects_list(loop.objects)
    }

def serialize_objects_list(objects):
    data = {}
    for i in range(0, len(objects)):
        true_obj = objects[i][1]
        data[i] = serialize_switch_set_data(true_obj) if isinstance(true_obj, switch.Switch) else serialize_station_set_data(true_obj)
    return data

def serialize_station_set_data(station):
    radius_angle = math.radians(station.angle)
    loop_radius = math.floor(station.loop.size / (2 * math.pi))
    return {
        'id': station.id,
        'x': station.loop.x + loop_radius * math.cos(radius_angle),
        'y': station.loop.y + loop_radius * math.sin(radius_angle),
        'name': station.name,
        'capacity': station.capacity
    }

def serialize_station_var_data(station):
    return {
    }

def serialize_switch_set_data(a_switch):
    switch_positions = get_switch_positions(a_switch)
    return {
        'id': a_switch.id,
        'nameIn': a_switch.my_loop.name + ' <= ' + a_switch.other_loop.name,
        'nameOut': a_switch.other_loop.name + ' => ' + a_switch.my_loop.name,
        'xIn': switch_positions[0],
        'yIn': switch_positions[1],
        'xOut': switch_positions[2],
        'yOut': switch_positions[3],
        'my_loop_name': a_switch.my_loop.name,
        'other_loop_name': a_switch.other_loop.name,
        'next_element_name': a_switch.next_element.name,
        'next_other_element_name': a_switch.next_element_other.name,
        'size': a_switch.size,
        'table': str(a_switch.table)
    }


def serialize_switch_var_data(a_switch):
    return {
    }


# def serialize_capsule(capsule_record):
#     return {
#         'id': capsule_record.id,
#         'x': capsule_record.x,
#         'y': capsule_record.y,
#         'travelerNumber': capsule_record.traveler_number
#     }

def serialize_capsule(a_capsule):
    x, y = get_capsule_position(a_capsule)
    return {
        'id': a_capsule.id,
        'x': x,
        'y': y,
        'travelerNumber': len(a_capsule.travelers),
        'destination': a_capsule.destination.name if a_capsule.destination is not None else "None",
        'loop': a_capsule.loop.name,
        'current_element': a_capsule.current_element.name,
        'next_element': a_capsule.next_element.name
    }


def get_segment_trip_angle(loop, current_element, next_element):
    if type(current_element) is switch.Switch:
        current_element_angle = get_switch_angle(loop, current_element)
    else:
        current_element_angle = current_element.angle

    if type(next_element) is switch.Switch:
        next_element_angle = get_switch_angle(loop, next_element)
    else:
        next_element_angle = next_element.angle

    if None in (current_element_angle, next_element_angle):
        return 0

    abs_difference = math.fabs(current_element_angle - next_element_angle)
    return min(abs_difference % 360, math.fabs(360 - abs_difference) % 360)


def get_element_angle(loop, element):
    if type(element) is switch.Switch:
        angle = get_switch_angle(loop, element)
        return angle

    return element.angle


def get_switch_angle(loop, a_switch):
    if a_switch.my_loop == loop:
        return a_switch.angle_my_loop

    if a_switch.other_loop == loop:
        return a_switch.angle_other_loop


def get_capsule_position(capsule):
    """
    :param capsule:
    :return: (x, y)
    """
    if capsule.current_element is capsule.next_element:
        # In this case, current_element can only be a switch
        t = capsule.get_segment_trip_percentage()
        x_in, y_in, x_out, y_out = get_switch_positions(capsule.current_element)
        return x_in * (1 - t) + x_out * t, y_in * (1 - t) + y_out * t
    else:
        # In this case, current_element and next_element can be station or switch
        angle = get_element_angle(capsule.loop, capsule.current_element)
        angle = (angle, 0)[angle is None]
        segment_trip_angle = get_segment_trip_angle(capsule.loop, capsule.current_element, capsule.next_element)
        segment_trip_angle = (segment_trip_angle, 0)[segment_trip_angle is None]
        percent_trip_angle = capsule.get_segment_trip_percentage() * segment_trip_angle
        radius_angle = math.radians(angle - percent_trip_angle)
        loop_radius = math.floor(capsule.loop.size / (2 * math.pi))
        return capsule.loop.x + math.cos(radius_angle) * loop_radius, capsule.loop.y + math.sin(
            radius_angle) * loop_radius


def get_switch_positions(a_switch):
    """
    :param a_switch:
    :return: (x_in, y_in, x_out, y_out)
    """
    radius_angle_loop_in = math.radians(a_switch.angle_my_loop)
    radius_angle_loop_out = math.radians(a_switch.angle_other_loop)
    loop_in_radius = math.floor(a_switch.my_loop.size / (2 * math.pi))
    loop_out_radius = math.floor(a_switch.other_loop.size / (2 * math.pi))
    x_in = a_switch.my_loop.x + math.cos(radius_angle_loop_in) * loop_in_radius
    y_in = a_switch.my_loop.y + math.sin(radius_angle_loop_in) * loop_in_radius
    x_out = a_switch.other_loop.x + math.cos(radius_angle_loop_out) * loop_out_radius
    y_out = a_switch.other_loop.y + math.sin(radius_angle_loop_out) * loop_out_radius
    return x_in, y_in, x_out, y_out
