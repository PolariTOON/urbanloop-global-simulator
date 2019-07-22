"""
Type de noeud du sous-graphe du réseau qui représente un garage où sont stocker des pods
"""

from ...tokens.pod import Pod
from .step import Step


class Shed(Step):
    def __init__(self, env, id, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, **kwargs)
        pods = pods or {
            "count": 0,
            "max": 0
        }
        pods["count"] = pods["count"] or 0
        pods["max"] = pods["max"] or 0
        element_of_loop = element_of_loop or {
            "loop": 0,
            "element": 0
        }
        element_of_loop["loop"] = element_of_loop["loop"] or 0
        element_of_loop["element"] = element_of_loop["element"] or 0
        self._pods = [Pod(env, self, 0, True) for k in range(pods["count"])]
        self._capacity = pods["max"]
        self._element_of_loop = element_of_loop

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "type": "shed",
            "pods": {
                "count": len(self._pods),
                "max": self._capacity
            }
        })
        return dict

    def to_element_of_loop(self):
        return self._element_of_loop

    @property
    def pods(self):
        return self._pods

    @property
    def capacity(self):
        return self._capacity

    def update(self):
        while True:
            while True:
                message = yield from self.read()
                if message is not None:
                    print("shed <%s>:" % self, message)
                if message is None:
                    break
                elif "pod_entry" in message["type"]:
                    pod = message["pod"]
                    yield from pod.write({
                        "author": self,
                        "type": "set_track_or_switch",
                        "track_or_switch": self
                    })
                    if pod.destination != self:  # la capsule ne fait que passer
                        yield from self.next.write({
                            "author": self,
                            "type": "pod_entry",
                            "pod": pod
                        })
                    else:  # la capsule va se garer dans le dépôt
                        self._pods.append(pod)
                        yield from pod.write({
                            "author": self,
                            "type": "docked"
                        })
                else:
                    break

