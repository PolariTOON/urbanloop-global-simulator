"""
C'est la représentation des arcs du sous-graphe du réseau
Cela permet 'avoir un capteur entre chaque section, tout comme dans un réseau réel idéal
"""

from .step import Step


class Sensor(Step):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "sensor",
            "name": self.name
        })
        return dict

    @property
    def pods(self):
        return []

    @property
    def name(self):
        return "sensor"

    def update(self):
        return
        yield
