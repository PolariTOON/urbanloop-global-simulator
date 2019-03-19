class AbstractArray():
    """
    Classe abstraite contenant le code commun aux classes StatsArray et StatsAverageArray
    """

    def __init__(self, description, unit=None):
        """
        constructeur
        """
        self._data = {}
        self._description = description
        self._unit = unit

    def _get_key(self, obj):
        """
        Renvoie la clé associée à un objet virtuel du réseau
        """
        return obj if isinstance(obj, type("")) else str(type(obj)) + "#" + str(obj.id)

    def get_info(self):
        """
        renvoie la description de cette liste
        """
        return self._description + ((" (en " + self._unit + ")") if self._unit != None else "")

    def get_unit(self):
        """
        renvoie l'unité de mesure de la grandeur enregistrée
        """
        return self._unit

    def get_keys(self):
        """
        renvoie la liste des objets concernés par ce type d'événements
        """
        keys = []
        for key in self._data:
            keys.append(key)
        return keys

    def get_keys_count(self):
        """
        renvoie le nombre d'objets ayant fourni des données
        """
        keys = []
        for key in self._data:
            keys.append(key)
        return len(keys)

    def get_ticks_count(self, obj):
        """
        renvoie le nombre d'événements associés à l'objet @param:obj
        """
        key = self._get_key(obj)
        return len(self._data[key])
