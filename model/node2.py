from .entity import Entity


class Node(Entity):
    def __init__(self, env, id, name=None, **kwargs):
        super().__init__(env, id, **kwargs)
        self._name = name or ""

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def pods(self):
        raise NotImplementedError()

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self._name
        })
        return dict
