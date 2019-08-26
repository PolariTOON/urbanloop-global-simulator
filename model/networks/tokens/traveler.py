from .token import Token


class Traveler(Token):
    def __init__(self, env, waiting_time=None, **kwargs):
        super().__init__(env, **kwargs)
        waiting_time = waiting_time or 0
        self._waiting_time = waiting_time

    @property
    def name(self):
        return super().name or "Traveler %d" % self.id

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict

    def update(self):
        return
        yield
