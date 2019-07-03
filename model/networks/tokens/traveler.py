from .token import Token


class Traveler(Token):
    def __init__(self, id, source=None, destination=None, **kwargs):
        super().__init__(source, destination, **kwargs)
        self.id = id

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
