from uuid import uuid4

from ..entity import Entity

class Token(Entity):
    def __init__(self, env, /, *, source=None, destination=None, **kwargs):
        if "id" in kwargs.keys():  # lorsqu'on recharge un pod on remet l'ancien id
            id0 = kwargs["id"]
            del kwargs["id"]
        else:
            id0 = uuid4().hex  # pour un nouvel objet on génère un id aléatoire (pour rendre l'id déterministe, utiliser un compteur / une seed et "uuid.UUID(int=[compteur ou valeur aléatoire], version=4)")
        super().__init__(env, id0, **kwargs)
        self._source = source or None
        self._destination = destination or None

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value

    @property
    def destination(self):
        return self._destination

    @destination.setter
    def destination(self, value):
        self._destination = value

    def serialize(self):
        dict = super().serialize()
        source = self.source
        destination = self.destination
        dict.update({
            "source": source,
            "destination": destination
        })
        return dict
