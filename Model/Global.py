# global
capsuleId = 0
stationId = 0

'''def getStationId(): 
  return stationId'''


class Destination:
  def __init__(self, station, distance, cost):
    self.station = station
    self.distance = distance
    self.cost = cost # estimated time cost
  
  def updateCost(self):
    # TODO
    return
