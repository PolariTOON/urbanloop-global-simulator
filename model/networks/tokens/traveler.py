from .token import Token


class Traveler(Token):
    def __init__(self, waiting_time, source=None, destination=None, **kwargs):
        super().__init__(source, destination, **kwargs)
        self._waiting_time = waiting_time

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
