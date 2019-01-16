from model.loop import Loop  # name, stations=None, switches=None
from model.station import Station  # name=None, capacity=1, previous_station=None, next_station=None, loop=None
from model.switch import Switch  # self, loop, previous_station, other_loop, next_station
from model import switch as MS
from settings import config

CONFIG_PATH = '../resources/settings.ini'
config.load(CONFIG_PATH)

nancy = Loop("Nancy")

villers = Loop("Villers-les-Nancy")

laxou = Loop("Laxou")

gare = Station("Gare", 100, None, None, nancy)
stan = Station("Stanislas", 100, gare, None, nancy)
artem = Station("ARTEM", 100, stan, gare, nancy)

velodrome = Station("Velodrome", 100, None, None, villers)
tncy = Station("TELECOM Nancy", 100, velodrome, None, villers)
eglise = Station("Eglise", 100, tncy, velodrome, villers)

auchan = Station("Gare", 100, None, None, laxou)
autoroute = Station("Entree_autoroute", 100, auchan, auchan, laxou)

la_na = Switch(laxou, nancy)
na_vi = Switch(nancy, villers)
vi_la = Switch(villers, laxou)
na_la = Switch(nancy, laxou)

laxou.switches = [la_na]
nancy.switches = [na_la, na_vi]
villers.switches = [vi_la]

MS.init()
print(la_na.id, la_na.permanent_table)
print(na_vi.id, na_vi.permanent_table)
print(vi_la.id, vi_la.permanent_table)
print(na_la.id, na_la.permanent_table)