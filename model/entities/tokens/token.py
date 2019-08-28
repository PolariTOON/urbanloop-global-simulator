from uuid import uuid4

from ..entity import Entity


class Token(Entity):
    def __init__(self, env, name=None, source=None, destination=None, **kwargs):
        super().__init__(env, uuid4().hex, **kwargs)
        self._name = name or ""
        self._source = source or None
        self._destination = destination or None

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        self._destination = value

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "source": self.source.to_element_of_loop(),
            "destination": self.destination.to_element_of_loop()
        })
        return dict
