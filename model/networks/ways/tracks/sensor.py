"""
C'est la représentation des arcs du sous-graphe du réseau
Cela permet 'avoir un capteur entre chaque section, tout comme dans un réseau réel idéal
"""

from .step import Step


class Sensor(Step):
    def __init__(self, previous_track, next_track, **kwargs):
        super().__init__(previous_track, next_track, **kwargs)

    def serialize(self):
        return super().serialize().update({
            "type": "sensor"
        })
