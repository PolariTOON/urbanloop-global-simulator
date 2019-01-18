import sys

from math import pi
from model.station import Station
from model.capsule import Capsule
from model.switch import Switch
from model.loop import Loop
from render.station_renderer import StationRenderer
from render.capsule_renderer import CapsuleRenderer
from render.switch_renderer import SwitchRenderer
from render.loop_renderer import LoopRenderer
from tkinter import Tk
from interface.simulator_frame import SimulatorFrame

path_to_add_array = sys.path[0].split("/")
del path_to_add_array[len(path_to_add_array)-1]
sys.path.append("/".join(path_to_add_array))


# TODO baptiste specification + menage


# window
window = Tk()
window["bg"]="#00FF00"
window.geometry("800x800+100+100")

w = SimulatorFrame(window)
w.grid()
w.rowconfigure(0,weight=1)
w.rowconfigure(1,weight=1)
w.rowconfigure(2,weight=1)
w.columnconfigure(0,weight=1)
w.columnconfigure(1,weight=1)
w.columnconfigure(2,weight=1)

# stations
s = Station(angle=90)
for i in range(1, 15):
    Station()
s2 = Station(angle=0)
print(s.name)
print(s2.name)
sr = StationRenderer(s, w)
sr2 = StationRenderer(s2, w)
scv = sr.canvas
scv2 = sr2.canvas
scv.grid(row=2, column=2)
scv2.grid(row=1,column=1)

# capsules
c = Capsule()
c2 = Capsule()
cr = CapsuleRenderer(c,w)
cr2 = CapsuleRenderer(c2,w)
ccv = cr.canvas
ccv2 = cr2.canvas
ccv.grid(row=0,column=0)
ccv2.grid(row=0,column=1)

# switches
sw = Switch(angle=180)
swr = SwitchRenderer(sw,w)
swcv = swr.canvas
swcv.grid(row=1,column=0)

# loop
l = Loop("oklm",coordinates=[1000,1000],size=300*pi)
l.objects = [s2, sw, s]
lr = LoopRenderer(l,w)
lcv = lr.canvas
lcv.grid(row=2,column=1)

w.mainloop()
