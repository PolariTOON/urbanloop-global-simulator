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

    @property
    def switch_out(self):
        return self._switch_out

    @switch_out.setter
    def switch_out(self, value):
        self._switch_out = value

    @property
    def discrete_places(self):
        return self._discrete_places

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

    def last_index_of(self, value):
        """
        :param value: l'élément dont on veut l'indice de la dernière occurence dans discrete_places
        :return: l'indice le plus grand où apparaît value dans discrete_places, -1 si value n'apparaît pas
        """
        index = -1
        for i in range(len(self._discrete_places)):
            if self._discrete_places[i] == value:
                index = i
        return index

    def full_decel(self, t, length):
        diff = t % self._step
        time = length / self.avg_speed
        return length / (time + diff)

    def backstep(self, first_place):
        """
        Envoie des ordres de vitesses aux capsules sur des places pour les décaler et
        ainsi permettre une insertion.
        :return: void
        """
        for index in range(first_place, len(self._discrete_places) - 2):
            # On décale les capsules à partir de la première place libre
            if self._discrete_places[index] is not None:
                pod = self._discrete_places[index]
                t = self.env.now
                speed = self.full_decel(t, self.beside.length + self.switch_out.c1_length)
                if self._discrete_places[index] is not None:
                    duration = (self.beside.length + self.switch_out.c1_length) / speed
                    yield from pod.write({
                        "author": self,
                        "type": "speed_a_while",
                        "speed": speed,
                        "pod": pod,
                        "duration": duration
                    })
                self._discrete_places[index] = self._discrete_places[index + 1]

    def update(self):
        # Les distances importantes sur la boucle où l'on peut s'inserer
        self._discretize_length = self.place_size * self.avg_speed / self.max_speed
        self._set_up_length = self._places_number * self.place_size
        self._finalisation_length = self.beside.length + self.switch_out.c1_length
        # Variables liées à la discrétisation
        self._discrete_places = [None for place in range(self._places_number)]
        self._step = self.place_size / self.avg_speed
        self._min_time = self.place_size / self.avg_speed
        self._max_time = self._min_time * self.saturation
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
