"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
        self._switch_in = None

        # Liaison de la route et des sections du pont
        self._beside.previous = self
        self._beside.sections[0].previous = self
        # Liaison inter aiguillage
        if self._beside.sections[-1].next is not None:
            self._switch_out = self._beside.sections[-1].next
            self._beside.sections[-1].next.switch_in = self

    @property
    def switch_in(self):
        return self._switch_in

    @switch_in.setter
    def switch_in(self, value):
        self._switch_in = value

    @property
    def name(self):
        return "switchOut"

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "type": "switch_out"
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
