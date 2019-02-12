import logging
import queue
import copy

from model import capsule
from model import station
from settings import config
from simulator import sim_loop

records = queue.Queue()
_limit = int(config.sim['default_record_size'])
_offset = 0


class SimRecord:
    def __init__(self):
        self.stations = copy.copy(station.get_stations())
        self.capsules = copy.copy(capsule.get_capsules())


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
    if records.empty():
        logging.error("The record queue is empty, impossible to get any")
        return None

    if records.qsize() <= int(_limit / 2) and sim_loop.is_paused():
        sim_loop.run_simulation()

    record = None
    for i in range(_offset + 1):
        record = records.get_nowait()
        if records.empty():
            return record
    return record
