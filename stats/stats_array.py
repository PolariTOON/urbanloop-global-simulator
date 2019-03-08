from stats import abstract_array

class StatsArray(abstract_array.AbstractArray):
  """
  Classe de tableaux enregistrants les ticks auxquels se produisent des évènements relatifs à un objet
  Chaque StatsArray symbolise un événement différent
  Cette classe ne sert que pour les compteurs: elle n'enregistre que des ticks.
  """
  
  def add(self, tick, obj):
    """
    permet d'enregistrer l'évènement s'étant produit au tick @param:tick pour l'objet @param:obj
    """
    key = self._get_key(obj)
    try:
      self._data[key].append(tick)
    except KeyError:
      self._data[key] = []
      self._data[key].append(tick)
  
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

  def get_value_between(self, obj, tick1, tick2):
    """
    renvoie le nombre d'événements apparus entre les dates @param:tick1 et @param:tick2
    """
    start = 0
    end = 0
    key = self._get_key(obj)
    ticks = self.get_ticks(key)
    
    for tick in ticks:
      if tick >= tick1:
        start = tick
        break
    for tick in ticks[::-1]:
      if tick <= tick2:
        end = tick
        break
    
    return len(ticks[start:end+1])