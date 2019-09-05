from math import floor
from random import random
from simpy.events import Process, Timeout
from simpy.resources.store import Store, StoreGet, StorePut


class Entity:
    def __init__(self, env, id, name=None, **kwargs):
        self._env = env
        self._id = id
        self._name = name or ""
        self._store = Store(env)
        Process(self._env, self.update())

    @property
    def env(self):
        return self._env

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

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
        print(self.name, "  --  ", message["author"].name, "  --  ", message["type"])
        return message

    def update(self):
        raise NotImplementedError()

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id
        }
