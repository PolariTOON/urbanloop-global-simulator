"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, env, id, margin_min, pod_size, saturation, places_number, **kwargs):
        super().__init__(env, id, margin_min, pod_size, saturation, **kwargs)
        self._switch_out = None
        # Liaison de la route et des sections du pont
        self._beside.next = self
        self._beside.sections[-1].next = self
        # Liaison inter aiguillage
        if self._beside.sections[0].previous is not None:
            self._switch_out = self._beside.sections[0].previous
            self._switch_out._switch_in = self
            self._beside.sections[0].previous.switch_in = self

        self._places_number = places_number
        # Les distances importantes sur la boucle où l'on peut s'inserer
        self._discretize_length = self.margin * self.max_speed() / (self.max_speed() - self.avg_speed)
        self._set_up_length = self._places_number * self.place_size
        self._finalisation_length = self.beside.length + self.switch_out.c1_length

    @property
    def switch_out(self):
        return self._switch_out

    @switch_out.setter
    def switch_out(self, value):
        self._switch_out = value

    @property
    def name(self):
        return "switchIn"

    @property
    def length(self):
        return 0

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
                    print(self.name, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:
                    pod = message["pod"]
                    self._pods.append(pod)
                    track = pod.track_or_switch.previous.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })
                elif "pod_exit" == message["type"]:
                    pod = message["pod"]
                    self._pods.remove(pod)
                else:
                    raise ValueError("Invalid message")
