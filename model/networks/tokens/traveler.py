from .token import Token


class Traveler(Token):
    def __init__(self):
        super().__init__(self)

    def serialize(self):
        return super().serialize().update({})
