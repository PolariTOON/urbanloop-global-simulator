from .token import Token
from .traveler import Traveler


class Pod(Token):
    def __init__(self, env, track_or_switch, pod_speed, position=None, travelers=None, speed_restore=None, length_before_restore=None, length_before_turn=None, turn=None, **kwargs):
        super().__init__(env, **kwargs)
        self._position = position or 0
        travelers = travelers or {
            "count": 0,
            "max": 0
        }
        travelers["count"] = travelers["count"] or 0
        travelers["max"] = travelers["max"] or 0
        self._travelers = [Traveler(env, 0) for k in range(travelers["count"])]
        self._capacity = travelers["max"]
        self._priority = 0  # TODO : à enlever
        self._track_or_switch = track_or_switch
        self._speed = pod_speed
        self._turn = turn or False
        self._length_before_turn = length_before_turn or None
        self._length_before_restore = length_before_restore or None
        self._speed_restore = speed_restore or None

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def travelers(self):
        return self._travelers

    @travelers.setter
    def travelers(self, value):
        self._travelers = value

    @property
    def capacity(self):
        return self._capacity

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        self._priority = value

    @property
    def track_or_switch(self):
        return self._track_or_switch

    @track_or_switch.setter
    def track_or_switch(self, value):
        self._track_or_switch = value

    @property
    def name(self):
        return super().name or "Pod %s" % self.id

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def speed_restore(self):
        return self._speed_restore

    @property
    def length_before_restore(self):
        return self._length_before_restore

    @property
    def length_before_turn(self):
        return self._length_before_turn

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "name": self.name,
            "position": self.position,
            "travelers": {
                "count": len(self.travelers),
                "max": self.capacity
            },
            "speed_restore": self.speed_restore,
            "length_before_restore": self.length_before_restore,
            "length_before_turn": self.length_before_turn,
            "speed": self.speed
        })
        return dict

    def add_traveler(self, traveler):
        self._travelers.append(traveler)
        print("Traveler %s gets in capsule %d" % (traveler.id, self.id), traveler.source, self.destination)

    def update(self):
        """
        Fonction qui gère le processus "pod", à chaque tour d'événement simpy les actions sont exécutées
        :return: void
        """
        while True:
            # Gestion du décalage et de la discrétisation : on reprend la vitesse moyenne après avoir parcouru la bonne distance
            if self._length_before_restore is not None:
                if self._length_before_restore > 0:
                    self._length_before_restore -= self._speed * self.env.sim_tick
                else:
                    self._length_before_restore = None
                    if self._speed_restore is not None:
                        self._speed = self._speed_restore
                        self._speed_restore = None

            # La capsule avance
            if self._speed != 0:
                self._position += self._speed * self.env.sim_tick

            # La capsule s'insère et tourne si elle en a reçu l'ordre
            if type(self._track_or_switch).__name__ == "SwitchOut" and self._turn and self._position >= self._length_before_turn:
                self.position -= self._length_before_turn
                self._track_or_switch = self._track_or_switch.beside.sections[0]
                yield from self._track_or_switch.write({
                    "author": self,
                    "type": "pod_entry",
                    "pod": self
                })
                self._turn = False
                self._length_before_turn = None

            # Gestion du changement de piste ou d'aiguillage : comme pour le prototype, la
            # capsule indique à la piste/l'aiguillage sur laquelle/lequel elle rentre
            if self._position > self._track_or_switch.length and self._speed != 0:
                bridge_to_switch = False
                self._position -= self._track_or_switch.length
                t = self._position / self._speed
                if type(self._track_or_switch).__name__ == "SwitchOut" or type(self._track_or_switch).__name__ == "SwitchIn":
                    self._track_or_switch = self._track_or_switch.next.sections[0]
                else:
                    if type(self._track_or_switch).__name__ == "Section":
                        if self._track_or_switch.is_bridge:
                            # la capsule va entrer sur un aiguillage entrant par un pont
                            bridge_to_switch = True
                    self._track_or_switch = self._track_or_switch.next
                self._position = t * self._track_or_switch.speed
                if bridge_to_switch:
                    yield from self._track_or_switch.write({
                        "author": self,
                        "type": "pod_entry_from_bridge",
                        "pod": self
                    })
                else:
                    yield from self._track_or_switch.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": self
                    })

            # Gestion des messages reçus
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "speed" == message["type"]:
                    # Ordre de changement de vitesse
                    self._speed = message["speed"]
                elif "passing" == message["type"]:
                    self._track_or_switch = self._track_or_switch.next
                    yield from self._track_or_switch.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": self
                    })
                elif "passing_from_switch" == message["type"]:
                    self._track_or_switch = self._track_or_switch.next.sections[0]
                    yield from self._track_or_switch.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": self
                    })
                elif "docked" == message["type"]:
                    # La capsule s'arrête dans une gare ou un dépôt
                    self._speed = 0
                elif "insert" == message["type"]:
                    # Ordre d'insertion, la capsule est autorisée à tourner
                    # une distance avant le pont est donnée
                    self._turn = True
                    self._length_before_turn = message["length_before_turn"]
                elif "speed_a_while" == message["type"]:
                    # Ordre de vitesse lors d'un décalage pour laisser une capsule s'insérer
                    # Ou lors d'une discrétisation
                    # La capsule prend une vitesse sur une certaine distance puis reprend la vitesse moyenne
                    self._speed = message["speed"]
                    self._length_before_restore = message["length_before_restore"]
                    self._speed_restore = message["speed_restore"]
                elif "departure" == message["type"]:
                    # La capsule part d'un dépôt ou d'une gare
                    destination = message["destination"]
                    self._destination = destination
                    self._source = self._track_or_switch
                    self._speed = self._track_or_switch.next.speed
                else:
                    raise ValueError("Invalid message")
