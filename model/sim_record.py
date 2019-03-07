from model import capsule
from model import queue
from settings import config
from settings import json_serializer
from settings import simlog
from simulator import sim_loop

records = queue.Queue()
_limit = int(config.sim['default_record_size'])
_offset = 2
from json import dumps


def gentest():
    yield dumps([json_serializer.serialize_capsule(a_capsule) for a_capsule in capsule.get_capsules()])


class SimRecord:
    def __init__(self):
        self.test = gentest()
        # self.current_tick = sim_loop.get_current_tick()
        # self.time_record = json_serializer.serialize_time()
        # self.stations_record = [json_serializer.serialize_station_var_data(a_station) for a_station in
        #                         station.get_stations()]
        # self.switches_record = []
        # self.capsules_record = [json_serializer.serialize_capsule(a_capsule) for a_capsule in capsule.get_capsules()]
        # self.warehouses_record = [json_serializer.serialize_warehouse_var_data(a_warehouse) for a_warehouse in
        #                           warehouse.get_warehouses()]
        self.current_tick = []
        self.time_record = []
        self.stations_record = []
        self.switches_record = []
        self.capsules_record = [CapsuleRecord(a_capsule) for a_capsule in capsule.get_capsules()] # TODO : vérifier ça !
        self.warehouses_record = []


def change_queue_size(limit=_limit):
    """
    Change the limit of the record queue
    :param limit: The desired limit for the record queue
    """
    global _limit
    _limit = limit


def change_queue_offset(offset=0):
    """
    The queue offset represents how many records of the simulation you want to skip at each frame
    of the graphic interface.
    :param offset: The desired offset
    """
    global _offset
    _offset = offset


def put_record():
    """
    Put a new record of the simulation in the record queue. If the limit is reached, the simulation is paused.
    """
    records.put(SimRecord())

    if records.qsize() >= _limit:
        sim_loop.pause_simulation()


def get_record():
    """
    Get a record of the simulation from the record queue. If the simulation was paused and the record queue is
    mid-empty, the simulation will restart in order to refill the record queue.
    """
    global records
    if is_empty():
        simlog.error("The record queue is empty, impossible to get any")
        return None

    if records.qsize() <= int(_limit / 2) and sim_loop.is_paused():
        sim_loop.change_state(sim_loop.SimState.RUNNING)

    record = None
    for i in range(_offset + 1):
        record = records.get()
        if is_empty():
            return record
    return record


def is_empty():
    return records.is_empty()
