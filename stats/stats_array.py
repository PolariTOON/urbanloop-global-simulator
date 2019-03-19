from simulator import sim_loop
from stats import abstract_array


class StatsArray(abstract_array.AbstractArray):
    """
    Classe de tableaux enregistrants les ticks auxquels se produisent des évènements relatifs à un objet
    Chaque StatsArray symbolise un événement différent
    Cette classe ne sert que pour les compteurs: elle n'enregistre que des ticks.
    """

    def add(self, obj):
        """
        permet d'enregistrer l'évènement s'étant produit au tick actuel pour l'objet @param:obj
        """
        tick = sim_loop.get_simulated_time()
        key = self._get_key(obj)
        value = round(tick, 2)
        try:
            self._data[key].append(value)
        except KeyError:
            self._data[key] = []
            self._data[key].append(value)

    def get_ticks(self, obj):
        """
        renvoie les ticks des événements associés à l'objet @param:obj
        """
        key = self._get_key(obj)
        return self._data[key]

    def get_ticks_count(self, obj):
        """
        renvoie le nombre d'événements associés à l'objet @param:obj
        """
        key = self._get_key(obj)
        return len(self._data[key])

    def get_value_between(self, obj, start_tick, end_tick):
        """
        renvoie le nombre d'événements apparus entre les dates @param:tick1 et @param:tick2
        """
        key = self._get_key(obj)
        start = 0
        end = self.get_ticks_count(key) - 1
        ticks = self.get_ticks(key)

        for tick in ticks:
            if tick >= start_tick:
                start = tick
                break
        for tick in ticks[::-1]:
            if tick <= end_tick:
                end = tick
                break

        return len(ticks[start:end + 1])

    def extract(self):
        """
        renvoie un string pour l'extraction des stats
        """
        # init
        buffer = "# " + self.get_info() + "\n#\n"
        # contenu
        data = self._data
        for key in data:
            buffer += "# " + key + "\n"
            for value in data[key]:
                buffer += str(round(value, 2)) + ";"
            buffer = buffer[:-1]
            buffer += "\n#\n"
        # fermeture
        buffer += "#\n# end\n\n"
        return buffer
