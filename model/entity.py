from math import floor
from simpy.events import Process, Timeout
from simpy.resources.store import Store, StoreGet, StorePut
from random import random


class Entity:
    def __init__(self, env, id, **kwargs):
        self._env = env
        self._id = id
        self._store = Store(env)
        Process(env, self.update())

    @property
    def env(self):
        return self._env

    @property
    def id(self):
        return self._id

    def write(self, message):
        if message is None:
            raise ValueError()
        Process(self._env, self._pipe(message))
        return
        yield

    def _pipe(self, message):
        timeout = random() * (1 - (self._env.now - floor(self._env.now)))
        yield Timeout(self._env, timeout)
        yield StorePut(self._store, message)

    def read(self):
        (timeout, getter) = (Timeout(self._env, 1 - (self._env.now - floor(self._env.now))), StoreGet(self._store))
        condition = yield timeout | getter
        if getter not in condition:
            getter.cancel()
            return None
        message = condition[getter]
        return message

    def update(self):
        return # TODO: implémenter
        yield
        raise NotImplementedError()

    def serialize(self):
        return {}
