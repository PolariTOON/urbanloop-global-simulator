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
        while True:
            while True:
                message = yield from self.read()
                if message is not None:
                    print("sensor <%s>:" % self, message)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:  # Un capsule ne s'arrête pas devant un capteur donc il passe directement l'info du passage à son suivant
                    pod = message["pod"]
                    yield from pod.write({
                        "author": self,
                        "type": "set_track_or_switch",
                        "track_or_switch": self
                    })
                    yield from self.next.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                else:
                    break
