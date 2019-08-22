"""
réuni des connexions pour former les switchs du réseau
"""
from .switch import Switch


class SwitchIn(Switch):
    def __init__(self, env, id, margin_min, pod_size, max_speed, places_number, **kwargs):
        super().__init__(env, id, margin_min, pod_size, max_speed, **kwargs)
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
        self._discretize_length = None
        self._set_up_length = None
        self._finalisation_length = None
        self._discrete_places = None
        self._step = None
        self._min_time = None
        self._max_time = None
        self._pod_to_add = None
        self._cursor = 0
        self._first_place = 0

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
    def first_place(self):
        return self._first_place

    @property
    def c2_length(self):
        return self._discretize_length + self._set_up_length + self._finalisation_length

    @property
    def length(self):
        return self.c2_length + 10

    @property
    def finalisation_length(self):
        return self._finalisation_length

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
        for i in range(self._first_place - self._places_number, self._first_place - 1):
            if self._discrete_places[i] == value:
                index = i
        return index

    def full_decel(self, length):
        diff = self._step
        time = length / self.avg_speed
        return length / (time + diff)

    def backstep(self, begin):
        """
        Envoie des ordres de vitesses aux capsules sur des places pour les décaler et
        ainsi permettre une insertion. On commence le décalage à l'indice begin.
        :return: void
        """
        x = (self._cursor % 1) * self.place_size
        time_to_shift = (self.place_size - x) / self.avg_speed
        speed = self.place_size / time_to_shift
        for index in range(self._first_place + begin - self._places_number, self._first_place - 2):
            # On décale les capsules à partir de la première place libre
            if self._discrete_places[index] is not None:
                pod = self._discrete_places[index]
                yield from pod.write({
                    "author": self,
                    "type": "speed_a_while",
                    "speed": speed,
                    "length_before_restore": self.place_size,
                    "speed_restore": self.avg_speed
                })
            self._discrete_places[index] = self._discrete_places[index + 1]
        self._discrete_places[self._first_place - 1] = None

    def update(self):
        # Les distances importantes sur la boucle où l'on peut s'inserer
        self._discretize_length = self.place_size * self.max_speed / (self.max_speed - self.avg_speed)
        self._set_up_length = self._places_number * self.place_size
        self._finalisation_length = self._places_number * self._places_number * self.max_speed / self.avg_speed
        # Maj de la vitesse du pont
        section = self.beside.sections[0]
        section.speed = max(section.speed, self.avg_speed * section.length / self._finalisation_length)
        # Variables liées à la discrétisation
        self._discrete_places = [None for place in range(self._places_number)]
        self._step = self.place_size / self.avg_speed
        self._switch_out.set_c1_length()
        while True:
            self._cursor = (self._cursor - self.avg_speed * self.env.sim_tick / self.place_size) % self._places_number
            if int(self._cursor) != self._first_place:
                # Le curseur a dépassé une nouvelle place, on avance le rouage
                # pod_to_add est None si pas de capsule à insérer dans le tableau
                # Si une capsule etait dans la dernière place alors elle disparaît
                self._discrete_places[self._first_place] = self._pod_to_add
                self._pod_to_add = None
            self._first_place = int(self._cursor)
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    # Notification à la section précédente que la capsule n'y est plus
                    pod = message["pod"]
                    self._pods.append(pod)
                    track = pod.track_or_switch.previous.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })

                    # Discrétisation de la capsule
                    x = (self._cursor % 1) * self.place_size
                    time_to_discretize = (self.place_size - x) / self.avg_speed
                    speed = self._discretize_length / time_to_discretize
                    self._pod_to_add = pod
                    yield from pod.write({
                        "author": self,
                        "type": "speed_a_while",
                        "length_before_restore": self._discretize_length,
                        "speed": speed,
                        "speed_restore": self.avg_speed
                    })
                elif "pod_entry_from_bridge" == message["type"]:
                    # notification au pont que la capsule n'y est plus
                    pod = message["pod"]
                    self._pods.append(pod)
                    track = pod.track_or_switch.beside.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })
                    yield from pod.write({
                        "author": self,
                        "type": "speed",
                        "speed": self.avg_speed
                    })
                elif "pod_exit" == message["type"]:
                    pod = message["pod"]
                    self._pods.remove(pod)
                else:
                    raise ValueError("Invalid message")
