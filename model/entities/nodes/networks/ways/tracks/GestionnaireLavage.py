# Un gestionnaire par réseau, donc par simulation
# Il faut donc une classe instanciable
# Comme elle fait partie du réseau, nous choisissons de la mettre dans Network
from random import randint


class GestionnaireLavage:

    def __init__(
            self,
            network,
            **kwargs
    ):
        self.network = network
        self.liste_pods = self.network.pods

    def obtenirDestination(self, nom_station_source, categorie_destination="HangarLavage"):
        # nom_station_source pourrait être ustilisé dans une recherche plus élaborée
        if categorie_destination == "HangarLavage":
            destination = self.network.hangarsLavage[randint(0, len(self.network.hangarsRevision) - 1)].name
        elif categorie_destination == "HangarSimple":
            destination = self.network.hangarsSimples[randint(0, len(self.network.hangarsSimples) - 1)].name
        else:
            raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestination de GestionnaireLavage")
        return destination

    def podDoitAllerAuLavage(self, pod):
        if pod.doit_aller_au_lavage:
            return True
        return False

    def serialize(self):
        return {}
