from .switch import Switch


class SwitchOut(Switch):
    def __init__(self, env, id, margin_min, pod_size, max_speed, **kwargs):
        super().__init__(env, id, margin_min, pod_size, max_speed, **kwargs)
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
        self._length = None

    @property
    def switch_in(self):
        return self._switch_in

    @switch_in.setter
    def switch_in(self, value):
        self._switch_in = value

    @property
    def length(self):
        return self._length

    @property
    def routing_table(self):
        return self._routing_table

    @routing_table.setter
    def routing_table(self, value):
        self._routing_table = value

    @property
    def name(self):
        return super().name or "Switch \"out\" %d" % self.id

    def set_c1_length(self):
        self._length = self._switch_in.finalisation_length * self.speed / self._switch_in.speed - self._beside.sections[0].length * self.speed / self._beside.sections[0].speed
        if self._beside.length > self._switch_in.finalisation_length * self.max_speed / self._switch_in.speed:
            print("\u001b[31mLA LONGUEUR DU PONT", self._beside.sections[0].name, "NE RESPECTE PAS LES NORMES DU RESEAU, elle est superieur à :", self._switch_in.finalisation_length * self.max_speed / self._switch_in.speed, "mètres\u001b[0m")

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "switch_out",
            "length": self.length
        })
        return dict

    def _is_route(self, pod):
        """
        :param pod: la capsule dont on veut savoir si elle doit être routée
        :return: True si la capsule doit être aiguillée, False sinon
        """
        if pod.destination in self._routing_table:
            return True
        else:
            return False

    def update(self):
        """
        Gère le processus d'aiguillage sortant, à chaque tour d'événement simpy les actions sont exécutées
        :return: void
        """
        while True:
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "  --  ", message["author"].name, "  --  ", message["type"])
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    # Entrée d'une capsule, il faut prévenir la section précédente que la capsule est sortie
                    pod = message["pod"]
                    self._pods.append(pod)
                    track = pod.track_or_switch.previous.sections[-1]
                    yield from track.write({
                        "author": self,
                        "type": "pod_exit",
                        "pod": pod
                    })
                    # Régulation pour tomber sur une place si insertion
                    d = self._length - pod.position
                    x = self._switch_in.cursor
                    t = d / self.speed + (self._beside.length - x) / self._switch_in.speed
                    speed = d / t
                    yield from pod.write({
                        "author": self,
                        "type": "speed_a_while",
                        "speed": speed,
                        "length_before_restore": d,
                        "speed_restore": None
                    })
                    # routage si besoin
                    routing = self._is_route(pod)
                    if routing:
                        index = self.switch_in.last_index_of(None)
                        first_place = self._switch_in.first_place
                        if index == first_place or index == -1:
                            # On ne peut pas insérer la capsule
                            pass
                        elif index == first_place - 1:
                            # On insert la capsule sur la dernière place
                            yield from pod.write({
                                "author": self,
                                "type": "insert",
                                "length_before_turn": self._length
                            })
                        else:
                            # On procède au décalage pour insérer la capsule
                            self.switch_in.backstep(index)
                            # On envoie un message indiquant que la voiture doit aller sur le pont
                            # La voiture s'insère alors sur la dernière place
                            yield from pod.write({
                                "author": self,
                                "type": "insert",
                                "length_before_turn": self._length
                            })
                elif "pod_exit" == message["type"]:
                    pod = message["pod"]
                    self._pods.remove(pod)
                elif "update_routing" == message["type"]:
                    new_table = message["table"]
                    self._routing_table = new_table
                else:
                    raise ValueError("Invalid message")
