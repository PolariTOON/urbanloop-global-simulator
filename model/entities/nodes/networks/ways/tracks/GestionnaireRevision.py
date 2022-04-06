# Un gestionnaire par réseau, donc par simulation
# Il faut donc une classe instanciable
# Comme elle fait partie du réseau, nous choisissons de la mettre dans Network
from random import randint


class GestionnaireRevision:
    LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT = 2000
    LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT = 2000

    @classmethod
    def genererDistanceAleatoire(cls):
        return randint(0, 2*cls.LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT)

    @classmethod
    def genererTempsAleatoire(cls):
        return randint(0, 2*cls.LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT)

    def __init__(
            self,
            network,
            limite_distance_parcourue_avant_revision=LIMITE_DISTANCE_PARCOURUE_AVANT_REVISION_DEFAUT,
            limite_temps_ecoule_avant_revision=LIMITE_TEMPS_ECOULE_AVANT_REVISION_DEFAUT
    ):
        self.network = network
        self.limite_distance_parcourue_avant_revision = limite_distance_parcourue_avant_revision
        self.limite_temps_ecoule_avant_revision = limite_temps_ecoule_avant_revision
        self.liste_pods = self.network.pods

    def obtenirDestination(self, nom_station_source, categorie_destination="HangarRevision"):
        # nom_station_source pourrait être ustilisé dans une recherche plus élaborée
        if categorie_destination == "HangarRevision":
            destination = self.network.hangarsRevision[randint(0, len(self.network.hangarsRevision) - 1)].name
        elif categorie_destination == "HangarSimple":
            destination = self.network.hangarsSimples[randint(0, len(self.network.hangarsSimples) - 1)].name
        else:
            raise ValueError(f"Catégorie {categorie_destination} non traitée dans obtenirDestinationHangarRevision")
        return destination

    def podDoitAllerEnRevision(self, pod):
        if \
                pod.distance_depuis_revision >= self.limite_distance_parcourue_avant_revision or \
                pod.temps_depuis_revision >= self.limite_temps_ecoule_avant_revision:
            return True
        return False

    def serialize(self):
        return {
            "limite_distance_parcourue_avant_revision": self.limite_distance_parcourue_avant_revision,
            "limite_temps_ecoule_avant_revision": self.limite_temps_ecoule_avant_revision
        }
