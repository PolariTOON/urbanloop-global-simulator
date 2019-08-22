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
        self._pods = [Pod(env, self, 0) for k in range(pods["count"])]
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
                    print(self.name, "||", message["type"], "||", message["author"].name)
                if message is None:
                    break
                elif "pod_entry" == message["type"]:
                    pod = message["pod"]
                    yield from self._parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
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
                elif "pod_exit" == message["type"]:
                    pass
                else:
                    raise ValueError("Invalid message")

