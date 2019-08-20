from settings import simlog
from .token import Token
from .traveler import Traveler


class Pod(Token):
    def __init__(self, env, track_or_switch, pod_speed, is_docked, position=None, travelers=None, **kwargs):
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
        self._priority = 0  # TODO
        self._track_or_switch = track_or_switch
        self._speed = pod_speed
        self._is_docked = is_docked
        self._on_beside = False
        self._turn = False
        self._length_before_turn = None
        self._speed_bridge = None
        self._length_before_restore = None
        self._speed_restore = None

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def is_docked(self):
        return self._is_docked

    @is_docked.setter
    def is_docked(self, value):
        self._is_docked = value

    @property
    def travelers(self):
        return self._travelers

    @travelers.setter
    def travelers(self, value):
        self._travelers = value

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
        return "POD %s" % self.id

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def on_beside(self):
        return self._on_beside

    @on_beside.setter
    def on_beside(self, value):
        self._on_beside = value

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "id": self.id,
            "name": self.name,
            "position": self._position,
            "travelers": {
                "count": len(self._travelers),
                "max": self._capacity
            }
        })
        return dict

    def add_traveler(self, traveler):
        self._travelers.append(traveler)
        simlog.info("Traveler %s gets in capsule %d" % (traveler.id, self.id), traveler.source, self.destination)

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
                    self._speed = self._speed_restore
                    self._speed_restore = None

            # La capsule avance
            if not self._is_docked and self._speed != 0:
                self._position += self._speed * self.env.sim_tick

            # La capsule s'insère et tourne
            if self._turn and self._position >= self._length_before_turn:
                self.position -= self._length_before_turn
                self._track_or_switch = self._track_or_switch.beside.sections[0]
                self._speed = self._speed_bridge
                yield from self._track_or_switch.write({
                    "author": self,
                    "type": "pod_entry_bridge",
                    "pod": self
                })
                self._turn = False
                self._speed_bridge = None
                self._length_before_turn = None

            # Gestion du changement de piste ou d'aiguillage : comme pour le prototype, la
            # capsule indique à la piste/l'aiguillage sur laquelle/lequel elle rentre
            if self._position > self._track_or_switch.length:
                bridge_to_switch = False
                self._position -= self._track_or_switch.length
                if str(type(self._track_or_switch)) == "<class 'model.networks.ways.switch_out.SwitchOut'>" or str(
                        type(self._track_or_switch)) == "<class 'model.networks.ways.switch_in.SwitchIn'>":
                    self._track_or_switch = self._track_or_switch.next.sections[0]
                else:
                    if str(type(self._track_or_switch)) == "<class 'model.networks.ways.tracks.section.Section'>" and self._track_or_switch.is_bridge:
                        # la capsule va entrer sur l'aiguillage entrant par un pont
                        bridge_to_switch = True
                        self._position += self._track_or_switch.next.c2_length
                    self._track_or_switch = self._track_or_switch.next
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
                if message is not None:
                    print(self.name, self.id, "||", message["type"], "||", message["author"].name, message["author"].id)
                if message is None:
                    break
                elif "speed" == message["type"]:
                    # Ordre de changement de vitesse
                    self._speed = message["speed"]
                elif "docked" == message["type"]:
                    # Ordre d'arrêt dans un dépôt ou une gare
                    self._speed = 0
                    self._is_docked = True
                elif "insert" == message["type"]:
                    # Ordre d'insertion, la capsule est autorisée à tourner
                    # une vitesse à prendre sur le pont et une distance avant le pont sont données
                    self._turn = True
                    self._speed_bridge = message["speed"]
                    self._length_before_turn = message["length_before_turn"]
                elif "speed_a_while" == message["type"]:
                    # Ordre de vitesse lors d'un décalage pour laisser une capsule s'insérer
                    # Ou lors d'une discrétisation
                    # La capsule prend une vitesse sur une certaine distance puis reprend la vitesse moyenne
                    self._speed = message["speed"]
                    self._length_before_restore = message["length_before_restore"]
                    self._speed_restore = message["speed_restore"]
                else:
                    raise ValueError("Invalid message")
