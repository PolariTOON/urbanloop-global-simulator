#! /usr/bin/env python3
# coding: utf-8

class Destination:
  def __init__(self, station, distance, cost):
    self.station = station
    self.distance = distance
    self.cost = cost # estimated time cost
  
  def updateCost(self):
    # TODO
    return