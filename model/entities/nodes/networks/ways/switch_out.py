from .switch import Switch


class SwitchOut(Switch):
    """Classe modélisant un aiguillage sortant
    Elle gère une partie de l'algorithme d'aiguillage"""
    def __init__(self, env, id, margin_min, pod_size, max_speed, stat_or_shed=None, **kwargs):
        if "pods" in kwargs:
            kwargs["pods"] = []
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
        self._stat_or_shed = stat_or_shed
        self._failed_insertion_since_last_minute = 0

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

    def get_failed_insertion_since_last_minute_and_reset(self):
        nb = self._failed_insertion_since_last_minute
        self._failed_insertion_since_last_minute = 0
        return nb

    @property
    def stat_or_shed(self):
        return self._stat_or_shed

    def set_c1_length(self):
        # TODO : cela ne concerne que le cas d'un bridge entre 2 loops, il faut ajouter le cas d'une dérivation vers une station/shed
        # TODO : vérifier si ce n'est pas grave d'autoriser une longueur de 0.0
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
        return pod.destination in self._routing_table

    def update(self):
        return

    def handle_message(self, message):
        if "pod_entry" == message["type"]:
            # Entrée d'une capsule, il faut prévenir la section précédente que la capsule est sortie
            pod = message["pod"]
            self._pods.append(pod)
            track = pod.track_or_switch.previous.sections[-1]
            track.write({
                "author": self,
                "type": "pod_exit",
                "pod": pod
            })
            # Régulation pour tomber sur une place si insertion
            d = self._length - pod.position
            x = self._switch_in.cursor
            t = d / self.speed + (self._beside.length - x) / self._switch_in.speed
            speed = d / t
            pod.write({
                "author": self,
                "type": "speed_a_while",
                "speed": speed,
                "length_before_restore": d,
                "speed_restore": None
            })
            # routage si besoin
            routing = self._is_route(pod)
            if routing:
                # déviation vers une station/shed
                if len(self._beside.steps) > 0 and type(self._beside.steps[0]).__name__ in ["Station", "Shed"]:
                    station_or_shed = self._beside.steps[0]
                    if station_or_shed.is_available():
                        pod.write({
                            "author": self,
                            "type": "insert"
                        })
                # pont vers une autre boucle
                index = self.switch_in.last_index_of(None)
                first_place = self._switch_in.first_place
                if index == first_place or index == -1:
                    # On ne peut pas insérer la capsule
                    #print("\t\t\033[4;31mInsertion capsule impossible\u001B[0m", pod.name[:8], self.name, "\t\t(switchout l.122)\n")
                    self._failed_insertion_since_last_minute += 1
                    pass
                elif index == first_place - 1:
                    # On insère la capsule sur la dernière place
                    pod.write({
                        "author": self,
                        "type": "insert"
                    })
                else:
                    # On procède au décalage pour insérer la capsule
                    self.switch_in.backstep(index)
                    # On envoie un message indiquant que la voiture doit aller sur le pont
                    # La voiture s'insère alors sur la dernière place
                    pod.write({
                        "author": self,
                        "type": "insert"
                    })
        elif "pod_exit" == message["type"]:
            pod = message["pod"]
            self._pods.remove(pod)
        elif "update_routing" == message["type"]:
            new_table = message["table"]
            self._routing_table = new_table
        else:
            raise ValueError("Invalid message")
