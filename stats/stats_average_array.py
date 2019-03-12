from stats import abstract_array
from simulator import sim_loop

class StatsAverageArray(abstract_array.AbstractArray):
  """
  Classe de tableaux enregistrants les couples [valeur;tick] associés aux évènements relatifs à un objet
  Chaque StatsAverageArray symbolise un événement différent
  """
  
  def add(self, value, obj):
    key = self._get_key(obj)
    try:
      self._data[key]
    except KeyError:
      self._data[key] = []
    tick = sim_loop.get_simulated_time()
    self._data[key].append((tick, value))
  
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
    REPRENDRE
    """
    key = self._get_key(obj)
    return self._data[key][start:end+1]
  
  def get_values_count_between(self, obj, start, end):
    """
    renvoie le nombre d'évènements associés à l'objet @param:obj
    REPRENDRE
    """
    key = self._get_key(obj)
    return len(self.get_values_between(obj, start, end))

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
      for couple in data[key]:
        buffer += str(couple[0]) + "-" + str(couple[1]) + ";"
      buffer = buffer[:-1]
      buffer += "\n#\n"
    # fermeture
    buffer += "#\n# end\n"
    return buffer

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

  # global stats
  def get_global_count(self):
    """
    renvoie le nombre de données récoltées
    """
    keys = self.get_keys()
    cpt = 0
    for key in keys:
      cpt += self.get_values_count(key)
    return cpt

  def get_global_count_between(self, start, end):
    """
    renvoie le nombre de données récoltées entre deux dates
    """
    keys = self.get_keys()
    cpt = 0
    for key in keys:
      cpt += self.get_values_count_between(key, start, end)
    return cpt

  def get_global_min(self):
    """
    renvoie la valeur minimum de l'ensemble des objets
    """
    keys = self.get_keys()
    global_min = float('inf')
    for key in keys:
      tmp_min = self.get_min(key)
      if tmp_min < global_min:
        global_min = tmp_min
    return global_min
  
  def get_global_min_between(self, start, end):
    """
    renvoie la valeur minimum de l'ensemble des objets entre deux dates
    """
    keys = self.get_keys()
    global_min = float('inf')
    for key in keys:
      tmp_min = self.get_min_between(key, start, end)
      if tmp_min < global_min:
        global_min = tmp_min
    return global_min

  def get_global_max(self):
    """
    renvoie la valeur maximum de l'ensemble des objets
    """
    keys = self.get_keys()
    global_max = -float('inf')
    for key in keys:
      tmp_max = self.get_max(key)
      if tmp_max > global_max:
        global_max = tmp_max
    return global_max
  
  def get_global_max_between(self, start, end):
    """
    renvoie la valeur maximum de l'ensemble des objets entre deux dates
    """
    keys = self.get_keys()
    global_max = -float('inf')
    for key in keys:
      tmp_max = self.get_max_between(key, start, end)
      if tmp_max > global_max:
        global_max = tmp_max
    return global_max

  def get_global_average(self):
    """
    renvoie la valeur moyenne des objets
    """
    keys = self.get_keys()
    global_average = 0
    for key in keys:
      global_average += self.get_average(key)
    return global_average / self.get_keys_count()
  
  def get_global_average_between(self, start, end):
    """
    renvoie la valeur moyenne des objets entre deux dates
    """
    keys = self.get_keys()
    global_average = 0
    for key in keys:
      global_average += self.get_average_between(key, start, end)
    return global_average / self.get_keys_count()
  
  def get_global_standard_deviation(self):
    """
    renvoie l'écart-type des objets
    """
    keys = self.get_keys()
    sd = 0
    average = self.get_global_average()
    for key in keys:
      for value in self.get_values(key):
        sd += (value - average)**2
    sd /= self.get_global_count()
    return sd **.5

  def get_global_standard_deviation_between(self, start, end):
    """
    renvoie l'écart-type des objets entre deux dates
    """
    keys = self.get_keys()
    sd = 0
    average = self.get_global_average_between(start, end)
    for key in keys:
      for value in self.get_values_between(key, start, end):
        sd += (value - average)**2
    sd /= self.get_global_count_between(start, end)
    return sd **.5