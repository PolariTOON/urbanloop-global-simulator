"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
        self._switch_in = None
        self._c1_to_insert = 50
        self._insert_to_end = 101
        # Liaison de la route et des sections du pont
        self._beside.previous = self
        self._beside.sections[0].previous = self
        # Liaison inter aiguillage
        if self._beside.sections[-1].next is not None:
            self._switch_in = self._beside.sections[-1].next
            self._switch_in._switch_out = self
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

    @property
    def length(self):
        return self._c1_to_insert + self._insert_to_end

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
                    print(self.name, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:
                    pod = message["pod"]
                    self._pods.append(pod)
                    if pod.track_or_switch != self:  # petite correction (j'espere temporaire!!)
                        pod.track_or_switch = self
                    track = pod.track_or_switch.previous.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })
                    yield from self.parent.write({
                        "author": self,
                        "type": "routing",
                        "pod": pod
                    })
                elif "pod_passing" == message["type"]:
                    pass
                elif "insert" == message["type"]:
                    pod = message["pod"]
                    pods_discretized = self._switch_in.pods_discretized
                    if None in pods_discretized:
                        index_to_see = int((self._c1_to_insert - pod.position + self._beside.length) / self.d_min)  # décalage de place à faire sur le temps qu'il va s'écouler entre maintenant et le moment où la capsule sera potentiellement insérée
                        if pods_discretized[self._switch_in.index_to_insert + 1 - index_to_see] is None or pods_discretized[self._switch_in.index_to_insert - index_to_see] is None:
                            yield from pod.write({
                                "author": self,
                                "type": "turn",
                                "distance": self._c1_to_insert - pod.position
                            })
                        else:
                            for index in range(len(pods_discretized) - 2, 0, -1):
                                place = pods_discretized[index]
                                if place is not None:
                                    l_shift = self.d_min
                                    d_discr = self.average_speed * l_shift / (self.limit_speed - self.average_speed)
                                    discr_speed = self.average_speed * (d_discr + l_shift) / d_discr
                                    time_to_discretize = {"time": d_discr / discr_speed, "average_speed": self.average_speed}
                                    yield from place.write({
                                        "author": self,
                                        "type": "discretize",
                                        "speed": discr_speed,
                                        "time": time_to_discretize,
                                        "place": place + 1
                                    })
                                else:  # On donne un ordre de vitesse à la capsule pour qu'elle rejoigne une place de discrétisation
                                    yield from pod.write({
                                        "author": self,
                                        "type": "turn"
                                    })
                    else:  # la capsule n'est pas aiguillée et refait un tour de boucle
                        pass
                elif "pod_exit" == message["type"]:
                    pod = message["pod"]
                    self._pods.remove(pod)
                else:
                    raise ValueError("Invalid message")
