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
        self._track_or_switch = track_or_switch  # TODO
        self._speed = pod_speed
        self._is_docked = is_docked

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
        return "pod n° %s" % self.id

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    def serialize(self):
        dict = super().serialize()
        dict.update({
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
        time_to_discretize = None
        while True:
            # Si la capsule est dans un aiguillage est qu'elle est en train de se discrétiser
            # on met à jour le vitesse si elle s'est placée après le bon temps
            if time_to_discretize is not None:
                time_to_discretize["time"] -= self.env.sim_tick
                if time_to_discretize["time"] <= 0:
                    self._speed = time_to_discretize["average_speed"]
                    self.track_or_switch.write({
                        "author": self,
                        "type": "end_discretized",
                        "pod": self
                    })
            # La capsule avance
            if not self._is_docked and self._speed != 0:
                self._position += self._speed * self.env.sim_tick

            # Gestion du changement de piste ou d'aiguillage : comme pour le prototype, la
            # capsule indique à la section sur laquelle elle rentre qu'elle y est
            if self._position > self._track_or_switch.length:
                self._position -= self._track_or_switch.length
                if str(type(self._track_or_switch)) == "<class 'model.networks.ways.switch_out.SwitchOut'>" or str(type(self._track_or_switch)) == "<class 'model.networks.ways.switch_in.SwitchIn'>":
                    self._track_or_switch = self._track_or_switch.next.sections[0]  # todo : ça peut être le beside si nécessaire
                else:
                    self._track_or_switch = self._track_or_switch.next
                yield from self._track_or_switch.write({
                    "author": self,
                    "type": "pod_entry",
                    "pod": self
                })

            # Gestion des messages reçus
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.id, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "speed" == message["type"]:
                    self._speed = message["speed"]
                elif "docked" == message["type"]:  # todo : correction à apporter ?
                    self._speed = 0
                    self._is_docked = True
                elif "ack" == message["type"]:
                    pass
                elif "set_track_or_bridge" == message["type"]:
                    track_or_switch = message["track_or_switch"]
                    self._track_or_switch = track_or_switch
                elif "discretize" == message["type"]:
                    discr_speed = message["speed"]
                    time_to_discretize = message["time"]
                    self._speed = discr_speed
                else:
                    pass
