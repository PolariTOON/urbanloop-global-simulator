class AbstractArray():
  """
  Classe abstraite contenant le code commun aux classes StatsArray et StatsAverageArray
  """
  def __init__(self, description):
    """
    constructeur
    """
    self._data = {}
    self._description = description

  
  def _get_key(self, obj):
    """
    Renvoie la clé associée à un objet virtuel du réseau
    """
    return obj if isinstance(obj, type("")) else str(type(obj)) + "#" + str(obj.id)
  
  def get_info(self):
    """
    renvoie la description de cette liste
    """
    return self._description
  
  def get_keys(self):
    """
    renvoie la liste des objets concernés par ce type d'événements
    """
    keys = []
    for key in self._data:
      keys.append(key)
    return keys
  
  def get_ticks_count(self, obj):
    """
    renvoie le nombre d'événements associés à l'objet @param:obj
    """
    key = self._get_key(obj)
    return len(self._data[key])