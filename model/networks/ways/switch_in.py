"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, env, id, **kwargs):
        super().__init__(env, id, **kwargs)
        self._switch_out = None
        self._c2_to_insert = 101
        self._bridge_to_insert = 10
        self._insert_to_end = 50
        self._margin = 2
        self._pod_size = 2
        discrete_places = int(((self._c2_to_insert + self._insert_to_end) / self.d_min))
        self._pods_discretized = [None for place in range(discrete_places)]
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
    def pods_discretized(self):
        return self._pods_discretized

    @property
    def name(self):
        return "switchIn"

    @property
    def length(self):
        return self._c2_to_insert + self._insert_to_end

    @property
    def d_min(self):
        return self._pod_size + self._margin

    @property
    def limit_speed(self):
        return 22.7

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

    def update(self):
        ticks_to_shift = self.d_min / (self.average_speed * self.env.sim_tick)
        tick_count = 0
        while True:
            if tick_count == ticks_to_shift:  # On fait avancer les places discrétisées
                tick_count = 0
                self._shift_discretized_pods()
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:  # Détéction d'une capsule => on lui envoie un ordre de vitesse pour qu'elle soit discrétisée
                    pod = message["pod"]
                    track = pod.track_or_switch.previous.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })
                    d_pod = pod.position
                    if self._pods_discretized[0] is not None:  # On positionnera la capsule sur la place qui suit (accélération)
                        d_place = tick_count * self.average_speed * self.env.sim_tick
                    else:  # On positionnera la capsule sur la place qui va suivre (décélération)
                        d_place = tick_count * self.average_speed * self.env.sim_tick - self.d_min  # todo : à vérifier pour la décélération
                    l_shift = d_place - d_pod  # Si on décélère on a un Ldécalage < 0 sinon > 0
                    d_discr = self.average_speed * l_shift / (self.limit_speed - self.average_speed)  # distance allouée pour rejoindre la place de discrétisation
                    discr_speed = self.average_speed * (d_discr + l_shift) / d_discr  # vitesse nécessaire pour rejoindre la place sur d_discr
                    time_to_discretize = {"time": d_discr / discr_speed, "average_speed": self.average_speed}
                    yield from pod.write({
                        "author": self,
                        "type": "discretize",
                        "speed": discr_speed,
                        "time": time_to_discretize
                    })
                elif "end_discretize" == message["type"]:
                    pod = message["pod"]
                    self._pods_discretized[0] = pod
                else:
                    pass
            tick_count += 1
