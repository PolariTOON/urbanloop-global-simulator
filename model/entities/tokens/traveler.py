from .token import Token


class Traveler(Token):
    def __init__(self, env, generation_time=None, waiting_time=None, boarding_time=None, **kwargs):
        super().__init__(env, **kwargs)
        self._waiting_time = waiting_time or 0
        self._generation_time = generation_time or 0
        self._boarding_time = boarding_time or 5

    @property
    def name(self):
        return super().name or "Traveler %d" % self.id

    @property
    def waiting_time(self):
        return self._waiting_time

    @classmethod
    def boarding_time(self):
        return self._boarding_time

    @property
    def boarding_time(self):
        return self._boarding_time

    def departure(self, time):
        self._waiting_time = time - self._generation_time
        return self._waiting_time

    def serialize(self):
        dict = super().serialize()
        return dict

    def update(self):
        return
        yield
