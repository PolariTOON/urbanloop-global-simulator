from math import hypot, nan
import sys

from .....tokens.pod import Pod
from .track import Track


class Section(Track):
    """Classe modélisant une section du réseau"""
    def __init__(self, env, id, margin_min, pod_size, is_bridge, speed=None, path=None, **kwargs):
        super().__init__(env, id, **kwargs)
        speed = speed or 0
        path = path or {
            "type": "line"
        }
        path["type"] = path["type"] or "line"
        self._is_bridge = is_bridge
        self._speed = speed
        self._path_type = path["type"]
        self._length = nan
        self._previous = None
        self._next = None
        self._pods = []
        self._margin = self._speed * (margin_min + pod_size) / 8.33 - pod_size  # 8.33 m/s = 30 km/h est la vitesse des plus petites boucles

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def is_bridge(self):
        return self._is_bridge

    @property
    def name(self):
        return super().name or "Section %d (%s -> %s)" % (self.id, self._previous.name, self._next.name)

    @property
    def path_type(self):
        return self._path_type

    @property
    def length(self):
        return self._length

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value
        other = self._next
        if value is None or other is None:
            self._length = nan
        else:
            self._length = hypot(other.x - value.x, other.y - value.y)  # TODO: gérer les autres types de chemins

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value
        other = self._previous
        if value is None or other is None:
            self._length = nan
        else:
            self._length = hypot(other.x - value.x, other.y - value.y)  # TODO: gérer les autres types de chemins

    @property
    def pods(self):
        return self._pods

    @property
    def weight(self):
        return self._length / self._speed

    @property
    def margin(self):
        return self._margin

    def update(self):
        while True:
            while True:
                message = yield from self.read()
                if message is None:
                    break
                elif "pod_exit" == message["type"]:
                    # Une capsule n'est plus dans la section
                    pod = message["pod"]
                    self._pods.remove(pod)
                elif "pod_entry" == message["type"]:
                    # Une capsule entre dans la section : il faut lui donner la bonne vitesse
                    # et il faut notifier le parent pour qu'il prévienne la piste/l'aiguillage précédente
                    pod = message["pod"]
                    self._pods.append(pod)
                    yield from self._parent.write({
                        "author": self,
                        "type": "pod_entry",
                        "pod": pod
                    })
                    yield from pod.write({
                        "author": self,
                        "type": "speed",
                        "speed": self._speed
                    })
                elif "speed_check" == message["type"]:
                    margin = self._speed * 5 / 100
                    if message["speed"] < self._speed - margin or message["speed"] > self._speed + margin:
                        yield from message["author"].write({
                            "author": self,
                            "type": "speed",
                            "speed": self._speed
                        })
                else:
                    raise ValueError("Invalid message")

    def serialize(self):
        dict = super().serialize()
        dict.update({
            "speed": self.speed,
            "path": {
                "type": self.path_type
            },
            "length": self.length
        })
        return dict

    def insert_pod(self, **pod):
        env = self._env
        pods = self._pods
        speed = pod["speed"]
        for k in range(len(pods)):
            if pods[k].position > pod["position"]:
                if "id" in pod:
                    del pod["id"]
                self._pods.insert(k, Pod(env, self, speed, **pod))
                return
        if "id" in pod:
            del pod["id"]
        self._pods.append(Pod(env, self, self._speed, **pod))

    def closest(self, pod):
        min_dist = sys.maxsize
        pod_return = None
        for pod_checked in self._pods:
            if pod_checked.id != pod.id:
                diff = pod_checked.position - pod.position
                if diff > 0 and diff < min_dist:
                    min_dist = diff
                    pod_return = pod_checked
        return pod_return
