from stats import stats_array as sa
from stats import stats_average_array as saa
from model import capsule as caps, loop, station as stat
from random import randint

c = caps.Capsule(None)
l = loop.Loop(name="example loop")
s = stat.Station()

array = sa.StatsArray("non-sense stat")
rd=0
for i in range(1, 50):
  tmp = randint(rd+1, rd+20)
  array.add(rd, c)
  tmp = randint(rd+1, rd+20)
  array.add(rd, l)
  tmp = randint(rd+1, rd+20)
  array.add(rd, s)
  rd = tmp
