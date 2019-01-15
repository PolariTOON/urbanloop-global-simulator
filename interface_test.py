from model.station import Station
from render.station_renderer import StationRenderer
from tkinter import Tk
from interface.simulator_frame import SimulatorFrame


# window
window = Tk()
window.geometry("200x200+100+100")

w = SimulatorFrame(window)
w.grid()
w.rowconfigure(0,weight=1)
w.rowconfigure(1,weight=1)
w.rowconfigure(2,weight=1)
w.columnconfigure(0,weight=1)
w.columnconfigure(1,weight=1)
w.columnconfigure(2,weight=1)

# objects
s = Station()
for i in range(1, 15):
    Station()
s2 = Station()
print(s.name)
print(s2.name)
sr = StationRenderer(s,w)
sr2 = StationRenderer(s2,w)
cv = sr.canvas
cv2 = sr2.canvas
cv.grid(row=2, column=2)
cv2.grid(row=1,column=1)

w.mainloop()
