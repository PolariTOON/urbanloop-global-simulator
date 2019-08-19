"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, env, id, margin_min, pod_size, saturation, c1_length, **kwargs):
        super().__init__(env, id, margin_min, pod_size, saturation, **kwargs)
        self._switch_in = None
        self._routing_table = None
        # Liaison de la route et des sections du pont
        self._beside.previous = self
        self._beside.sections[0].previous = self
        # Liaison inter aiguillage
        if self._beside.sections[-1].next is not None:
            self._switch_in = self._beside.sections[-1].next
            self._switch_in._switch_out = self
            self._beside.sections[-1].next.switch_in = self

        self._c1_length = c1_length

    @property
    def switch_in(self):
        return self._switch_in

    @switch_in.setter
    def switch_in(self, value):
        self._switch_in = value

    @property
    def c1_length(self):
        return self._c1_length

    @property
    def routing_table(self):
        return self._routing_table

    @routing_table.setter
    def routing_table(self, value):
        self._routing_table = value

    @property
    def name(self):
        return "switchOut"

    @property
    def length(self):
        return 0

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "type": "switch_out"
        })
        return dict

    def _is_route(self, pod):
        for moving_pod in self._routing_table:
            if moving_pod["pod"] == pod and self in moving_pod["way"]:
                return True
        return False

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
                    # routage si besoin
                    routing = self._is_route(pod)
                    if routing:
                        # TODO : Envoyer l'ordre de vitesse
                        pass
                elif "pod_exit" == message["type"]:
                    pod = message["pod"]
                    self._pods.remove(pod)
                else:
                    raise ValueError("Invalid message")
