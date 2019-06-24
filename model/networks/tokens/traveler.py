from .token import Token


class Traveler(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def serialize(self):
        dict = super().serialize()
        dict.update({})
        return dict
