import uuid

_loop_id = -1
_warehouse_id = -1
_station_id = -1
_switch_id = -1
_capsule_id = -1
_traveler_id = -1
_node_id = -1


def generate_unique():
    return uuid.uuid4().hex


def generate_loop_id():
    global _loop_id
    _loop_id += 1
    return _loop_id


def generate_warehouse_id():
    global _warehouse_id
    _warehouse_id += 1
    return _warehouse_id


def generate_station_id():
    global _station_id
    _station_id += 1
    return _station_id


def generate_switch_id():
    global _switch_id
    _switch_id += 1
    return _switch_id


def generate_capsule_id():
    global _capsule_id
    _capsule_id += 1
    return _capsule_id


def generate_traveler_id():
    global _traveler_id
    _traveler_id += 1
    return _traveler_id

def generate_node_id():
    global _node_id
    _node_id += 1
    return _node_id
