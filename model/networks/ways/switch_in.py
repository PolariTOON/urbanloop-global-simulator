"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
        self._switch_out = None

        # Liaison de la route et des sections du pont
        self._beside.next = self
        self._beside.sections[-1].next = self
        # Liaison inter aiguillage
        if self._beside.sections[0].previous is not None:
            self._switch_out = self._beside.sections[0].previous
            self._beside.sections[0].previous.switch_in = self

    @property
    def switch_out(self):
        return self._switch_out

    @switch_out.setter
    def switch_out(self, value):
        self._switch_out = value

    @property
    def name(self):
        return "switchIn"

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "type": "switch_in"
        })
        return dict

    def update(self):
        while True:
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self, "||", message)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:  # pour le moment la capsule ne fait que de passer todo : algo aiguillage à un plus haut niveau
                    pod = message["pod"]
                    track = pod.track_or_switch.previous.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })
                else:
                    pass

