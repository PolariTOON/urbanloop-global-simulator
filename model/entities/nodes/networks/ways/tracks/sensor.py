from .step import Step


class Sensor(Step):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "sensor"
        })
        return dict

    @property
    def pods(self):
        return []

    @property
    def name(self):
        return super().name or "Sensor %d" % self.id

    def update(self):
        while True:
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "pod_entry" == message["type"]:  # Un capsule ne s'arrête pas devant un capteur donc il passe directement l'info du passage à son suivant
                    pod = message["pod"]
                    yield from self._parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                    yield from pod.write({
                        "author": self,
                        "type": "passing"
                    })
                elif "pod_exit" == message["type"]:
                    pass
                else:
                    raise ValueError("Invalid message")
