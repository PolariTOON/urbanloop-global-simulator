import math

from model import switch
from simulator import converter
from simulator import sim_loop


def serialize_time():
    return {
        'day': converter.now_to_day(),
        'time': converter.seconds_to_string(converter.now_to_seconds())
    }


def serialize_loop(a_loop):
    return {
        'uuid': str(a_loop.uuid),
        'id': a_loop.id,
        'name': a_loop.name,
        'x': a_loop.x,
        'y': a_loop.y,
        'radius': math.floor(a_loop.size / (2 * math.pi)),
        'size': a_loop.size,
        'objects': serialize_objects_list(a_loop.objects)
    }


def serialize_objects_list(objects):
    data = {}
    for i in range(0, len(objects)):
        obj = objects[i][1]
        obj_type = objects[i][0]
        if "station" in obj_type:
            data[i] = "Station " + obj.name
            # data[i] = serialize_switch_set_data(true_obj) if isinstance(true_obj, switch.Switch)
            # else serialize_station_set_data(true_obj)
        elif "warehouse" in obj_type:
            data[i] = "Warehouse %d in %s " % (obj.id, obj.loop.name)
            #  data[i] = serialize_warehouse_set_data(obj)
        elif "out" in obj_type:
            data[i] = "Switch out #%d to %s" % (obj.id, obj.loop.name)
        elif "in" in obj_type:
            data[i] = "Switch in #%d from %s" % (obj.id, obj.loop.name)
    return data


def serialize_station_set_data(a_station):
    radius_angle = math.radians(a_station.angle)
    loop_radius = get_loop_radius(a_station.loop)
    return {
        'uuid': str(a_station.uuid),
        'id': a_station.id,
        'x': a_station.loop.x + loop_radius * math.cos(radius_angle),
        'y': a_station.loop.y + loop_radius * math.sin(radius_angle),
        'name': a_station.name,
        'capacity': a_station.capacity,
        'outerCircle': a_station.loop.name,
        'type': a_station.get_string_type(),
        'next_element': a_station.next_element.name,
        'nb_travelers': a_station.traveler_queue.qsize(),
        'nb_capsules': a_station.capsule_queue.qsize(),
        'capsules': serialize_capsule_queue(a_station.capsule_queue)
    }


def serialize_warehouse_set_data(a_warehouse):
    radius_angle = math.radians(a_warehouse.angle)
    loop_radius = math.floor(a_warehouse.loop.size / (2 * math.pi))
    return {
        'uuid': str(a_warehouse.uuid),
        'id': a_warehouse.id,
        'x': a_warehouse.loop.x + loop_radius * math.cos(radius_angle),
        'y': a_warehouse.loop.y + loop_radius * math.sin(radius_angle),
        'name': a_warehouse.name,
        'capacity': a_warehouse.capacity,
        'outerCircle': a_warehouse.loop.name,
        'next_element': a_warehouse.next_element.name,
        'nb_capsules': a_warehouse.capsule_queue.qsize(),
        'capsules': serialize_capsule_queue(a_warehouse.capsule_queue)
    }


def serialize_capsule_queue(queue):
    capsules = {}
    # TODO fixer
    # capsules_list = queue.list()
    # for i in range(0, len(capsules_list)):
    #    capsules[i] = capsules_list[i].id
    return capsules


def serialize_station_var_data(a_station):
    return {
        'uuid': str(a_station.uuid),
        'name': a_station.name,
        'capacity': a_station.capacity,
        'outerCircle': a_station.loop.name,
        'type': a_station.get_string_type(),
        'next_element': a_station.next_element.name,
        'nb_travelers': a_station.traveler_queue.qsize(),
        'nb_capsules': a_station.capsule_queue.qsize(),
        'capsules': serialize_capsule_queue(a_station.capsule_queue)

    }


def serialize_warehouse_var_data(a_warehouse):
    return {
        'uuid': str(a_warehouse.uuid),
        'id': a_warehouse.id,
        'name': a_warehouse.name,
        'capacity': a_warehouse.capacity,
        'outerCircle': a_warehouse.loop.name,
        'next_element': a_warehouse.next_element.name,
        'nb_capsules': a_warehouse.capsule_queue.qsize(),
        'capsules': serialize_capsule_queue(a_warehouse.capsule_queue)
    }


def serialize_switch_set_data(a_switch):
    switch_positions = get_switch_positions(a_switch)
    return {
        'uuid': str(a_switch.uuid),
        'id': a_switch.id,
        'nameIn': a_switch.my_loop.name + ' -> ' + a_switch.other_loop.name,
        'nameOut': a_switch.other_loop.name + ' <- ' + a_switch.my_loop.name,
        # 'nameIn':  a_switch.id + ': ' + a_switch.my_loop.name + ' -> ' + a_switch.other_loop.name,
        # 'nameOut': a_switch.id + ': ' + a_switch.other_loop.name + ' <- ' + a_switch.my_loop.name,
        'xIn': switch_positions[0],
        'yIn': switch_positions[1],
        'xOut': switch_positions[2],
        'yOut': switch_positions[3],
        'my_loop_name': a_switch.my_loop.name,
        'other_loop_name': a_switch.other_loop.name,
        'next_element_name': a_switch.next_element.name,
        'next_other_element_name': a_switch.next_element_other.name,
        'size': a_switch.size,
        # 'table': str(a_switch.table)
    }


def serialize_switch_var_data(a_switch):
    return {
    }


def serialize_capsule(a_capsule):
    x, y = get_capsule_position(a_capsule)
    return {
        'uuid': str(a_capsule.uuid),
        'id': a_capsule.id,
        'x': x,
        'y': y,
        'travelerNumber': len(a_capsule.travelers),
        'destination': a_capsule.destination.name if a_capsule.destination is not None else "None",
        'outerCircle': a_capsule.loop.name,
        'current_element': a_capsule.current_element.name,
        'next_element': a_capsule.next_element.name
    }


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


def get_loop_radius(loop):
    return loop.size / (2 * math.pi)


def get_capsule_position(capsule):
    """
    :param capsule:
    :return: (x, y)
    """
    if capsule.current_element is capsule.next_element:
        # In this case, current_element and next_element can only be switches
        t = capsule.get_segment_traveled_distance() / capsule.current_element.size
        x_in, y_in, x_out, y_out = get_switch_positions(capsule.current_element)
        return x_in * (1 - t) + x_out * t, y_in * (1 - t) + y_out * t
    else:
        # In this case, current_element and next_element can be station or switch
        angle = get_element_angle(capsule.loop, capsule.current_element)
        trip_angle = capsule.get_segment_traveled_angle()
        if capsule.loop.clockwise :
            radius_angle = math.radians(angle) + trip_angle
        else :
            radius_angle = math.radians(angle) - trip_angle
        loop_radius = get_loop_radius(capsule.loop)
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
