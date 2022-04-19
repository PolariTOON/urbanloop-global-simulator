# Un gestionnaire par réseau, donc par simulation
# Il faut donc une classe instanciable
# Comme elle fait partie du réseau, nous choisissons de la mettre dans Network
from random import randint


class GestionnaireLavage:
    TEMPS_LAVAGE_DEFAUT = 100

    def __init__(
            self,
            network,
            temps_lavage=None
    ):
        self._network = network
        self._temps_lavage = temps_lavage or GestionnaireLavage.TEMPS_LAVAGE_DEFAUT

        self._liste_pods = self._network.pods

    def serialize(self):
        return {
            "temps_lavage": self._temps_lavage
        }

    @property
    def temps_lavage(self):
        return self._temps_lavage

    def obtenirDestination(self, nom_station_source, categorie_destination="HangarLavage"):
        # nom_station_source pourrait être ustilisé dans une recherche plus élaborée
        if categorie_destination == "HangarLavage":
            destination = self._network.hangarsLavage[randint(0, len(self._network.hangarsRevision) - 1)].name
        elif categorie_destination == "HangarSimple":
            destination = self._network.hangarsSimples[randint(0, len(self._network.hangarsSimples) - 1)].name
        else:
            raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestination de GestionnaireLavage")
        return destination

    def podDoitAllerAuLavage(self, pod):
        if pod.doit_aller_au_lavage:
            return True
        return False
