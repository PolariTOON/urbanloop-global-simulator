from ....node import Node


class Track(Node):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
        self._parent = None

    @property
    def pods(self):
        raise NotImplementedError()

    @property
    def previous(self):
        raise NotImplementedError()

    @property
    def next(self):
        raise NotImplementedError()

    @property
    def length(self):
        return 0

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
