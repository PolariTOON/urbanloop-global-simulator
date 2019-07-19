from settings import simlog
from .token import Token
from .traveler import Traveler


class Pod(Token):
    def __init__(self, env, track_or_switch, speed, position=None, travelers=None, **kwargs):
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
        self._speed = speed

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
        while True:
            self._position += self._speed * self.env.sim_tick
            if self._position > self._track_or_switch.length:
                self._position -= self._track_or_switch.length
                yield from self._track_or_switch.write({
                    "author": self,
                    "type": "pod_exit",
                })
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "speed" in message["type"]:
                    self._speed = message["speed"]
                else:
                    break
