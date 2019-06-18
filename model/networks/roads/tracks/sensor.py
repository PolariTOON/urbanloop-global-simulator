"""
C'est la représentation des arcs du sous-graphe du réseau
Cela permet 'avoir un capteur entre chaque section, tout comme dans un réseau réel idéal
"""

from .step import Step


class Sensor(Step):
    def __init__(self, x, y):
        super().__init__(self)
        self.x = x
        self.y = y

    def serialize(self):
        return super().serialize().update({
            'type': 'sensor'
        })
