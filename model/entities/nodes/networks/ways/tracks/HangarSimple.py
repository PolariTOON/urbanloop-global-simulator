from .Hangar import Hangar


class HangarSimple(Hangar):
    """ Classe modélisant un dépôt, y est géré le départ des capsules, le réapprovisionnement et
    les interactions avec les autres éléments du réseau"""

    def __init__(self, env, id, departure_pods=None, pods=None, element_of_loop=None,
                 doiventAllerEnRevision=None,
                 doiventAllerAuLavage=None,
                 **kwargs):
        super().__init__(env, id, departure_pods, pods, element_of_loop, **kwargs)

        doiventAllerEnRevision = doiventAllerEnRevision or [False for _ in self._pods]
        doiventAllerAuLavage = doiventAllerAuLavage or [False for _ in self._pods]
        self._doiventAllerEnRevision = []
        self._doiventAllerAuLavage = []
        for i in range(len(self._pods)):
            if doiventAllerEnRevision[i]:
                self._doiventAllerEnRevision.append(self._pods[i])
            if doiventAllerAuLavage[i]:
                self._doiventAllerAuLavage.append(self._pods[i])

    def serialize(self):
        """sérialise les informations du dépôt"""
        dico = super().serialize()
        dico.update({
            "type": f"{self.__class__.__name__}",
            "doiventAllerEnRevision": [True if pod in self._doiventAllerEnRevision else False for pod in self._pods],
            "doiventAllerAuLavage": [True if pod in self._doiventAllerAuLavage else False for pod in self._pods]
        })
        return dico

    def attendDepartVers_RevisionOuLavage(self, pod):
        return pod in self._doiventAllerEnRevision or pod in self._doiventAllerAuLavage

    def doitAllerEn_RevisionOuLavage(self, pod):
        return self.gestionnaireRevision.podDoitAllerEnRevision(pod) or self.gestionnaireLavage.podDoitAllerAuLavage(pod)

    def send_pod(self, pod, destination):
        for p in self._departure_pods:
            if p == pod:
                raise Exception(p.name[:8] + " already in departure pods (HangarSimple)")
        pod.destination = destination
        self._departure_pods.append(pod)

    def update(self):
        """Fonction gérant le processus dépôt"""

        # p debut
        for pod in self._pods:
            if \
                    pod is not None and \
                            self.gestionnaireLavage.podDoitAllerAuLavage(pod) and \
                            pod not in self._doiventAllerAuLavage and \
                            pod not in self._doiventAllerEnRevision:
                pod.en_direction_lavage = True
                self._doiventAllerAuLavage.append(pod)
                print(f"Pod {pod.quickInfos_index} est prévu comme à laver")
            elif \
                    pod is not None and \
                            self.gestionnaireRevision.podDoitAllerEnRevision(pod) and \
                            pod not in self._doiventAllerEnRevision and \
                            pod not in self._doiventAllerAuLavage:
                pod.en_direction_revision = True
                self._doiventAllerEnRevision.append(pod)
                print(f"Pod {pod.quickInfos_index} est prévu comme à réviser")
        # p fin

        # Attente pour le prochain départ
        if self._wait != -1:
            self._wait += self.env.tick
            if self._wait > self.next.margin / self.next.speed:
                self._wait = -1

        for pod in self._doiventAllerEnRevision:
            if pod not in self._departure_pods:
                destination = self.gestionnaireRevision.obtenirDestinationDepuisHangarSimple(
                    categorie_destination="HangarRevision"
                )
                if pod.travelers != []:
                    raise ValueError(f"Pod {pod.quickInfos_index} doit aller en révision mais pod.travelers n'est pas None\nadresse {pod}")
                self.send_pod(pod, destination) # => self._departure_pods.append(pod) et pod.destination=destination
                print(f"Il est constaté dans HangarSimple {self.name} que Pod {pod.quickInfos_index} doit aller en révision\n\tIl lui est ordonné d'aller en révision à {destination}")
        for pod in self._doiventAllerAuLavage:
            if pod not in self._departure_pods:
                destination = self.gestionnaireLavage.obtenirDestinationDepuisHangarSimple(
                    categorie_destination="HangarLavage"
                )
                if pod.travelers != []:
                    raise ValueError(f"Pod {pod.quickInfos_index} doit aller au lavage mais pod.travelers n'est pas None\nadresse {pod}")
                self.send_pod(pod, destination)  # => self._departure_pods.append(pod) et pod.destination=destination
                print(
                    f"Il est constaté dans HangarSimple {self.name} que Pod {pod.quickInfos_index} doit aller au lavage\n\tIl lui est ordonné d'aller au lavage à {destination}")

        # Départ d'une capsule
        if self._departure_pods and self._wait == -1:
            self._wait = 0
            pod = self._departure_pods.pop(0)
            pod.during_departure = True
            destination = pod.destination
            pod.write({
                "author": self,
                "type": "departure",
                "destination": destination
            })
            # prévient le parent
            self.parent.write({
                "author": self,
                "pod": pod,
                "type": "departure",
                "destination": destination,
                "timestamp": self.env.time,
                "waiting_time": 0,
                "traveler": False
            })

    def handle_message(self, message):
        if "pod_entry" == message["type"]:
            pod = message["pod"]
            self._parent.write({
                "author": self,
                "type": "pod_entry",
                "pod": pod
            })
            if pod.destination == self.name:
                self._pods.append(pod)
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
                pod.write({
                    "author": self,
                    "type": "passing"
                })
        elif "pod_exit" == message["type"]:
            pod = message["pod"]
            if pod in self._pods:
                self._pods.remove(pod)
                if pod in self._doiventAllerEnRevision:
                    self._doiventAllerEnRevision.remove(pod)
                if pod in self._doiventAllerAuLavage:
                    self._doiventAllerAuLavage.remove(pod)
                pod.during_departure = False
            else:
                # dans ce cas, le pod n'était pas docked dans le shed,
                # et on accepte qu'il passe à travers.
                pass
        elif "refill" == message["type"]:
            station = message["station"]
            if len(self._pods) > 0 and len(self._pods) > len(self._departure_pods) + len(
                    self.pods_during_departure):  # on vérifie qu'il y a des pods et qu'il ne s'agit pas de pods déjà affectés à une station
                i = 0
                while i < len(self._pods) - 1 and (
                        self._pods[i] in self._departure_pods
                        or self._pods[i].during_departure
                        or self.gestionnaireRevision.podDoitAllerEnRevision(self._pods[i])
                        or self.gestionnaireLavage.podDoitAllerAuLavage(self._pods[i])
                ):
                    i += 1
                pod = self._pods[i]
                if (self._pods[i] in self._departure_pods
                        or self._pods[i].during_departure
                        or self.gestionnaireRevision.podDoitAllerEnRevision(self._pods[i])
                        or self.gestionnaireLavage.podDoitAllerAuLavage(self._pods[i])
                ) :
                    network = self.parent.parent
                    found_station = network.get_station_by_name(station)
                    if found_station is None:
                        import inspect
                        stack = inspect.stack()
                        the_class = stack[1][0].f_locals["self"].__class__.__name__
                        the_name = stack[1][0].f_locals["self"].name
                        the_method = stack[1][0].f_code.co_name
                        print(
                            f"méthode courante {self.name}.handle_message()-->refill appelée par {the_name}.{the_method}()")
                        print(f"auteur : {message['author']}")

                    found_station.down_incoming_pods()
                else :
                    #print("")
                    #print(f"Un pod se voit assigner la destination {station} lorsque le {self.__class__.__name__} {self.name} traite un refill")
                    #print("")
                    pod.destination = station
                    self._departure_pods.append(pod)
                    #print(f"{self.name} : pod ajouté à self._departure_pods")
                    #print(f"self._departure_pods = ")
                    #print(f"{self._departure_pods}")
            else:
                # on cherche la station concernée,
                # et on l'informe qu'elle ne recevra pas le pod.
                network = self.parent.parent
                found_station = network.get_station_by_name(station)
                if found_station is None:
                    import inspect
                    stack = inspect.stack()
                    the_class = stack[1][0].f_locals["self"].__class__.__name__
                    the_name = stack[1][0].f_locals["self"].name
                    the_method = stack[1][0].f_code.co_name
                    print(f"méthode courante {self.name}.handle_message()-->refill appelée par {the_name}.{the_method}()")
                    print(f"auteur : {message['author']}")

                found_station.down_incoming_pods()

        else:
            raise ValueError("Invalid message")
