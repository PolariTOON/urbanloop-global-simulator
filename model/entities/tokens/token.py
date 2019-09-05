from uuid import uuid4

from ..entity import Entity


class Token(Entity):
    def __init__(self, env, source=None, destination=None, **kwargs):
        super().__init__(env, uuid4().hex, **kwargs)
        self._source = source or None
        self._destination = destination or None

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
        source = self.source.element_of_loop
        destination = self.destination.element_of_loop
        dict.update({
            "source": source,
            "destination": destination
        })
        return dict
