from math import floor
from random import random
from simpy.events import Process, Timeout
from simpy.resources.store import Store, StoreGet, StorePut


class Entity:
    def __init__(self, env, id, name=None, **kwargs):
        self._env = env
        self._id = id
        self._name = name or ""
        if self._env.with_messages:
            self.write = self.write_1
            self._store = Store(env)
            Process(self._env, self.run())
        else:
            self.write = self.write_3
            self.read = self.read_3
            if self.updatable:
                self._env.updatable_entities.append(self)

    @property
    def env(self):
        return self._env

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id
        }

    # mode 3

    def write_3(self, message):
        if message is None:
            raise ValueError()
        self._env.messages.append( (self, message) )
        return

    def read_3(self, message):
        self.handle_message(message)
        return
    
    # mode 2

    def write_2(self, message):
        if message is None:
            raise ValueError()
        StorePut(self._store, message)
        return

    def read_2(self):
        (timeout, getter) = (Timeout(self._env, 1 - (self._env.now - floor(self._env.now))), StoreGet(self._store))
        condition = yield timeout | getter
        if getter not in condition:
            # Timeout -> envoi d'un update (= None)
            getter.cancel()
            return None
        message = condition[getter]
        return message

    # mode 1

    def write_1(self, message):
        if message is None:
            raise ValueError()
        Process(self._env, self._pipe(message))
        return

    def _pipe(self, message):
        timeout = random() *  (1 - (self._env.now - floor(self._env.now)))
        yield Timeout(self._env, timeout) # Timeout pour simuler la durée d'envoi du message
        yield StorePut(self._store, message)

    def read(self):
        (timeout, getter) = (Timeout(self._env, 1 - (self._env.now - floor(self._env.now))), StoreGet(self._store))
        condition = yield timeout | getter
        if getter not in condition:
            # Timeout -> envoi d'un update (= None)
            getter.cancel()
            return None
        message = condition[getter]
        # print("\t\t", self.name, "  --  ", message["author"].name, "  --  ", message["type"])
        return message

    def run(self):
        """
        Fonction qui gère le processus en mode "self._env.with_messages == True".
        A chaque tour d'événement simpy les actions sont exécutées
        :return: void
        """
        while True:
            self.update()
            # réception des messages
            while True:
                message = yield from self.read()
                if message is None:
                    break
                else:
                    self.handle_message(message)
    
    def updatable(self):
        """ Renvoie True si l'entity a besoin qu'on appelle son `update()`.
            Cela permet de ne pas avoir à appeler les `update()` de toutes les entités,
            et donc d'améliorer légèrement les performances.
        """
        raise NotImplementedError()
    
    def update(self):
        raise NotImplementedError()

    def handle_message(self):
        raise NotImplementedError()
