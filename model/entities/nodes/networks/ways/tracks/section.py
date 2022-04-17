from math import hypot, nan
import sys

from .GestionnaireRevision import GestionnaireRevision
from .....tokens.pod import Pod
from .shed import Shed
from .station import Station
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
        self._margin = self._speed * (margin_min + pod_size) / 8.33 - pod_size  # 8.33 m/s = 30 km/h est la vitesse des plus petites boucles -> TODO : à mettre à jour ?
        self._speed2 = speed

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
        _next = self._next
        if value is None or _next is None:
            self._length = nan
        else:
            self._length = hypot(_next.x - value.x, _next.y - value.y)

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value
        previous = self._previous
        if value is None or previous is None:
            self._length = nan
        else:
            self._length = hypot(previous.x - value.x, previous.y - value.y)

    @property
    def pods(self):
        return self._pods

    @property
    def weight(self):
        return self._length / self._speed

    @weight.setter
    def weight(self, value):
        self._weight = value

    @property
    def margin(self):
        return self._margin

    def fermeture_ouverture(self):
        """ fonction pour la fermeture de voie via l'interface web"""
        if self._speed == 0.000001:
            self._speed = self._speed2
        else:
            self._speed = 0.000001
        self.weight = self._length / self._speed

    @property
    def updatable(self):
        return False

    def update(self):
        return

    def handle_message(self, message):
        
        if "pod_exit" == message["type"]:
            # Une capsule n'est plus dans la section
            pod = message["pod"]
            if pod in self._pods:
                self._pods.remove(pod)
            else:
                #print("\u001B[31m [erreur pod non trouvé]", pod.name[:9], self.name, " (section l.103)\u001B[0m")
                print("\u001B[31m [erreur pod non trouvé]", pod, self.name, " (section l.118)\u001B[0m")
                print(message)
                print(pod.destination)
                
        elif "pod_entry" == message["type"]:
            # Une capsule entre dans la section : il faut lui donner la bonne vitesse
            pod = message["pod"]
            self._pods.append(pod)
            pod.write({
                "author": self,
                "type": "speed",
                "speed": self._speed
            })
            # on transmet le message à la Road
            self._parent.write({
                "author": self,
                "type": "pod_entry",
                "pod": pod
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
        diff = 0
        #On regarde dans la section si on trouve des capsules
        for pod_checked in self._pods:
            if pod_checked.id != pod.id:
                diff = pod_checked.position - pod.position
                if diff > 0 and diff < min_dist:
                    min_dist = diff
                    pod_return = pod_checked
        #Si on a pas trouvé de capsules on cherche dans la section suivante
        next = None
        same_section = True
        if not pod_return:
            if type(self.next).__name__ == "Switch":
                next = self.next.sections[0]
            elif type(self.next.next).__name__ == "Section":
                next = self.next.next
            if next:
                for pod_checked in next.pods:
                    diff = pod_checked.position + (self._length - pod.position)
                    if diff > 0 and diff < min_dist:
                        min_dist = diff
                        pod_return = pod_checked
                        same_section = False
        return pod_return, same_section
