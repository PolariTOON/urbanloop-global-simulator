from enum import Enum


class SimState(Enum):
    RUNNING = 0
    SLEEP = 1
    KILLED = 2
