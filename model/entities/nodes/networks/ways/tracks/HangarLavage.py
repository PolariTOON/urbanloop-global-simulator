from .Hangar import Hangar
from .shed import Shed


class HangarLavage(Hangar):
    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None, **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)


    def handle_message(self, message):
        if "pod_entry" == message["type"]:
            pod = message["pod"]
            self.parent.write({
                "author": self,
                "type": "pod_entry",
                "pod": pod
            })
            # la capsule va se garer dans la station s'il y a de la place
            if self._pods[0] is None:

                for i in range(len(self._pods) - 1, -1, -1):
                    if self._pods[i] is None:
                        self._pods[i] = pod
                        break

                self._incoming_pods -= 1
                if self._incoming_pods < 0:
                    print("\033[4;31mERROR: mauvais comptage des incoming pods\u001B[0m",
                          self._incoming_pods, " ", self.name, "\n\t\t(station l.277)")

                for t in pod.travelers:
                    t.disembark()

                pod.travelers = []
                pod.write({
                    "author": self,
                    "type": "docked"
                })
                self.parent.write({
                    "author": self,
                    "type": "docked",
                    "pod": pod,
                    "timestamp": self.env.time
                })
            else:
                print("ERROR: La station %s ne devrait pas être pleine.\n\t\t(station l.333)" % self.name)
                pod.write({  # "passing" fait passer le pod à travers la station
                    "author": self,
                    "type": "passing"
                })

        elif "pod_exit" == message["type"]:
            self._waiting_empty = False  # pour autoriser à nouveau la libération de pods
            pod = message["pod"]
            if pod not in self.pods:
                # pod passing
                return
            pod.during_departure = False
            if pod != self._pods[-1]:
                print("ERROR: a pod left without being in the front position.\n\t\t(station l.327)")
            for i in range(self._capacity - 1, 0, -1):  # on décale les autres pods vers l'avant
                # TODO : ne pas faire ce décalage si un passager est en train de monter
                #        (sinon la capsule bouge pendant que la personne monte dedans...)
                self._pods[i] = self._pods[i - 1]
                self._boarding[i] = self._boarding[i - 1]
            self._pods[0] = None
            self._boarding[0] = -1

        elif "empty" == message["type"]:
            pod = self._pods[-1]
            if pod is not None and self._boarding[
                -1] == -1 and not pod.during_departure and not pod in self._departure_pods:  # on libère un pod vide (pas None, n'a pas de passager et n'est pas déjà sur le point de partir)
                self.send_pod(pod, message["shed"].name)
                # "self._waiting_empty = False" est réalisé à la réception de "pod_exit"
            else:
                if pod is None:
                    print("\u001B[31mWARNING: ", self.name, ": pas de pod à libérer (station l.311)",
                          len(self._departure_pods), "\u001B[0m")
                self._waiting_empty = False

        else:
            raise ValueError("Invalid message received by a station: ", message)

