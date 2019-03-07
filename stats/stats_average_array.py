from stats import abstract_array

class StatsAverageArray(abstract_array.AbstractArray):
  """
  Classe de tableaux enregistrants les couples [valeur;tick] associés aux évènements relatifs à un objet
  Chaque StatsAverageArray symbolise un événement différent
  """
  
  def add(self, tick, value, obj):
    if self._data[obj] is None:
      self._data[obj] = []
    self._data[obj].add((tick, value))
  
  def get_values(self, obj):
    """
    renvoie les couples [tick; value] des évènements associés à l'objet @param:obj
    """
    key = self._get_key(obj)
    return self._data[key]
  
  def get_values_count(self, obj):
    """
    renvoie le nombre d'évènements associés à l'objet @param:obj
    """
    key = self._get_key(obj)
    return len(self._data[key])

  def get_values_between(self, obj, start, end):
    """
    renvoie les couples [tick; value] des évènements associés à l'objet @param:obj
    entre les dates @param:tick1 et @param:tick2
    """
    key = self._get_key(obj)
    return self._data[key][start:end+1]
  
  def get_values_count_between(self, obj, start, end):
    """
    renvoie le nombre d'évènements associés à l'objet @param:obj
    """
    key = self._get_key(obj)
    return len(self.get_values_between(obj, start, end))

  def get_min(self, obj):
    """
    renvoie la valeur min de l'échantillon
    """
    key = self._get_key(obj)
    min = float('inf')
    for couple in self.get_values(self._get_key(key)):
      value = couple[1]
      if value < min:
        min = value
    return min
  
  def get_min_between(self, obj, start, end):
    """
    renvoie la valeur min de l'échantillon entre deux dates
    """
    key = self._get_key(obj)
    min = float('inf')
    for couple in self.get_values_between(self._get_key(key), start, end):
      value = couple[1]
      if value < min:
        min = value
    return min
  
  def get_max(self, obj):
    """
    renvoie la valeur max de l'échantillon
    """
    key = self._get_key(obj)
    max = -float('inf')
    for value in self.get_values(self._get_key(key)):
      if value > max:
        max = value
    return max
  
  def get_max_between(self, obj, start, end):
    """
    renvoie la valeur max de l'échantillon entre deux dates
    """
    key = self._get_key(obj)
    max = -float('inf')
    for value in self.get_values_between(self._get_key(key), start, end):
      if value > max:
        max = value
    return max
  
  def get_average(self, obj):
    """
    renvoie la valeur moyenne de l'échantillon
    """
    key = self._get_key(obj)
    average = 0
    for value in self.get_values(self._get_key(key)):
      average += value
    return average / self.get_values_count(obj)

  def get_average_between(self, obj, start, end):
    """
    renvoie la valeur moyenne de l'échantillon entre deux dates
    """
    key = self._get_key(obj)
    average = 0
    for value in self.get_values_between(self._get_key(key), start, end):
      average += value
    return average / self.get_values_count_between(obj, start, end)

  def get_standard_deviation(self, obj):
    """
    renvoie l'écart-type de l'échantillon
    """
    key = self._get_key(obj)
    average = self.get_average(key)
    sd = 0
    for value in self.get_values(key):
      sd += (value - average)**2
    sd /= self.get_values_count(key)
    return sd**.5

  def get_standard_deviation_between(self, obj, start, end):
    """
    renvoie l'écart-type de l'échantillon entre deux dates
    """
    key = self._get_key(obj)
    average = self.get_average_between(key, start, end)
    sd = 0
    for value in self.get_values_between(key, start, end):
      sd += (value - average)**2
    sd /= self.get_values_count_between(key, start, end)
    return sd**.5
