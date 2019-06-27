from .token import Token


class Traveler(Token):
    def __init__(self, source=None, destination=None, **kwargs):
        super().__init__(source, destination, **kwargs)

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
