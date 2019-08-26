"""
Type de noeud du sous-graphe correspondant à une station d"arrêt
"""
from ...tokens.pod import Pod
from .step import Step

station_types = {
    "city": 0,
    "residential": 1,
    "activity": 2,
}


class Station(Step):
    def __init__(self, env, id, pods=None, travelers=None, station_type=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        travelers = travelers or 0
        station_type = station_type or station_types["city"]
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._average_waiting_time = travelers["average_waiting_time"]
        self._pods = [Pod(env, self, 0) for k in range(pods["count"])]
        self._capacity = pods["max"]
        if travelers["count"]:
            self._travelers = [self._average_waiting_time in range(travelers["count"])]  # cette liste représente une file des voyageurs en attente, elle est remplie par le temps d'attente de chacun
        else:
            self._travelers = []
        self._station_type = station_type
        self._element_of_loop = element_of_loop

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "station",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            },
            "travelers": {
                "count": len(self._travelers),
                "average_waiting_time": self._average_waiting_time
            },
            "station_type": self._station_type
        })
        return dict

    def to_element_of_loop(self):
        return self._element_of_loop

    @property
    def pods(self):
        return self._pods

    @property
    def travelers(self):
        return self._travelers

    @travelers.setter
    def travelers(self, value):
        self._travelers = value

    @property
    def type(self):
        return self._station_type

    @property
    def capacity(self):
        return self._capacity

    def update(self):
        while True:
            while True:
                message = yield from self.read()
                if message is not None:
                    print(self.name, "  --  ", message["author"].name, "  --  ", message["type"])
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    pod = message["pod"]
                    yield from self.parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                    # la capsule va se garer dans la station
                    if pod.destination == self:
                        self._pods.append(pod)
                        yield from pod.write({
                            "author": self,
                            "type": "docked"
                        })
                        yield from self.parent.write({
                            "author": self,
                            "type": "docked",
                            "pod": pod
                        })
                    else:
                        yield from pod.write({
                            "author": self,
                            "type": "passing"
                        })
                elif "pod_exit" == message["type"]:
                    pass
                else:
                    raise ValueError("Invalid message")
