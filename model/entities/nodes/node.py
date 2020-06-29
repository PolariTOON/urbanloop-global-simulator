from ..entity import Entity


class Node(Entity):
    def __init__(self, env, id, /, **kwargs):
        super().__init__(env, id, **kwargs)

    @property
    def pods(self):
        raise NotImplementedError()

    def serialize(self):
        dict = super().serialize()
        return dict
