"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
        self._switch_out = None
        self._c2_to_insert = 101
        self._insert_to_end = 50
        discrete_places = int(((self._c2_to_insert + self._insert_to_end) / self.d_min))
        self._pods_discretized = [None for place in range(discrete_places)]
        self._tick_count = 0
        # Liaison de la route et des sections du pont
        self._beside.next = self
        self._beside.sections[-1].next = self
        # Liaison inter aiguillage
        if self._beside.sections[0].previous is not None:
            self._switch_out = self._beside.sections[0].previous
            self._switch_out._switch_in = self
            self._beside.sections[0].previous.switch_in = self

    @property
    def switch_out(self):
        return self._switch_out

    @switch_out.setter
    def switch_out(self, value):
        self._switch_out = value

    @property
    def pods_discretized(self):
        return self._pods_discretized

    @property
    def name(self):
        return "switchIn"

    @property
    def length(self):
        return self._c2_to_insert + self._insert_to_end

    @property
    def index_to_insert(self):
        return int(self._c2_to_insert / self.d_min)

    @property
    def ticks_to_shift(self):
        return int(self.d_min / (self.average_speed * self.env.sim_tick))

    @property
    def tick_count(self):
        return self._tick_count

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "type": "switch_in"
        })
        return dict

    def _shift_discretized_pods(self):
        for index in range(len(self._pods_discretized) - 1, 0, -1):
            self._pods_discretized[index] = self._pods_discretized[index - 1]
        self._pods_discretized[0] = None

    def update(self):
        while True:
            for place in self._pods_discretized:
                if place is not None:
                    print(self._pods_discretized)
                    break
            if self._tick_count == self.ticks_to_shift:  # On fait avancer les places discrétisées
                self._tick_count = 0
                self._shift_discretized_pods()
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:  # Détéction d'une capsule => on lui envoie un ordre de vitesse pour qu'elle soit discrétisée si elle provient de la boucle
                    pod = message["pod"]
                    if pod.on_beside:  # La capsule provient du pont
                        pod.position = self._c2_to_insert # il faut que la capsule parcout la bonne distance
                        track = self._beside.sections[-1]
                        yield from track.write({
                            "author": self,
                            "type": "pod_exit",
                            "pod": pod
                        })
                        self._pods.append(pod)
                        d_pod = pod.position
                        if self._pods_discretized[self.index_to_insert] is None:
                            d_place = self._tick_count * self.average_speed * self.env.sim_tick + self.index_to_insert * self.d_min
                            place = self.index_to_insert
                        elif self._pods_discretized[self.index_to_insert + 1] is None:
                            d_place = self._tick_count * self.average_speed * self.env.sim_tick + (self.index_to_insert + 1) * self.d_min
                            place = self.index_to_insert + 1
                        else:
                            raise ValueError("Place must be None, bad insert")
                        l_shift = d_place - d_pod
                        d_discr = self.limit_speed * l_shift / (self.limit_speed - self.average_speed)
                        discr_speed = self.average_speed * (d_discr + l_shift) / d_discr
                        time_to_discretize = {"time": d_discr / discr_speed, "average_speed": self.average_speed}
                        yield from pod.write({
                            "author": self,
                            "type": "discretize",
                            "speed": discr_speed,
                            "time": time_to_discretize,
                            "place": place
                        })
                    else:  # La capsule provient de la boucle
                        track = pod.track_or_switch.previous.sections[-1]
                        yield from track.write({
                            "author": self,
                            "type": "pod_exit",
                            "pod": pod
                        })
                        d_pod = pod.position
                        if self._pods_discretized[0] is not None:  # On positionnera la capsule sur la place qui suit (accélération)
                            d_place = self._tick_count * self.average_speed * self.env.sim_tick
                            place = 1
                        else:  # On positionnera la capsule sur la place qui va suivre (décélération)
                            d_place = self._tick_count * self.average_speed * self.env.sim_tick - self.d_min
                            place = 0
                        l_shift = d_place - d_pod  # Si on décélère on a un Ldécalage < 0 sinon > 0
                        d_discr = self.limit_speed * l_shift / (self.limit_speed - self.average_speed)  # distance allouée pour rejoindre la place de discrétisation
                        discr_speed = self.average_speed * (d_discr + l_shift) / d_discr  # vitesse nécessaire pour rejoindre la place sur d_discr
                        time_to_discretize = {"time": d_discr / discr_speed, "average_speed": self.average_speed}
                        yield from pod.write({
                            "author": self,
                            "type": "discretize",
                            "speed": discr_speed,
                            "time": time_to_discretize,
                            "place": place
                        })
                elif "end_discretize" == message["type"]:
                    pod = message["pod"]
                    place = message["place"]
                    if self._pods_discretized[place] is None:
                        self._pods_discretized[place] = pod
                    else:
                        raise ValueError("bad discretize")
                elif "pod_exit" == message["type"]:
                    pod = message["pod"]
                    self._pods.remove(pod)
                else:
                    raise ValueError("Invalid message")
            self._tick_count += 1
