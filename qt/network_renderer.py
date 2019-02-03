
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPicture, QPainter, QColor
from PyQt5.QtCore import Qt, QRect
from math import pi, cos, sin

from settings import config
import model.loop as ML
import model.station as MST
import model.switch as MSW

class NetworkRenderer:
    def __init__(self, root):
        self.root = root
        self.config = config.interface
        self.outline_width = int(self.config["loop_outline_width"])
    
    def paint(self):
        paint = QPainter()
        paint.begin(self.root.image)
        paint.setRenderHint(QPainter.Antialiasing)
        # make loops
        for name in ML.all_loops:
            loop = ML.get_by_name(name)
            # make a circle
            r = loop.size / 2 / pi
            paint.setBrush(QColor(self.config["selected_color"] if self.root.selected_item == loop else self.config["loop_color"]))
            paint.drawEllipse(get_rect_for_loop(loop, 0))
            paint.setBrush(QColor("white"))
            paint.drawEllipse(get_rect_for_loop(loop, int(self.config["loop_outline_width"])))
            # make stations and switches for after painting loop
            self.fill_loop(loop, paint)
        # join loops between themselves
        self.join_loops()
        paint.setBrush(QColor("black"))
        paint.drawPoint(0,0)
        paint.drawPoint(7,50)
            
    def fill_loop(self, loop, paint):
        item_nbr = 0
        for obj in loop.objects:
            item_type = obj[0]
            item = obj[1]
            if (item != None):
                is_station = isinstance(item, MST.Station)
                if self.root.selected_item == item:
                    paint.setBrush(QColor(self.config["selected_color"]))
                else:
                    paint.setBrush(QColor(self.config["station_color" if is_station else "switch_color"]))
                paint.drawEllipse(get_rect_for_item(item, loop, 0, None if is_station else item_type))
                paint.setBrush(QColor("white"))
                outline_width = int(self.config["switch_outline_width"]) if isinstance(item, MSW.Switch) else int(self.config["station_outline_width"])
                rect = get_rect_for_item(item, loop, outline_width, None if is_station else item_type)
                paint.drawEllipse(rect)
                paint.drawText(rect.getCoords()[0], rect.getCoords()[1], "{0}".format(item_nbr))
                item_nbr+=1

    
    def join_loops(self):
        return

"""
return the rect in which @param loop
will be displayed. @param i represent
the outline width of the loop
"""
def get_rect_for_loop(loop, i):
    x = loop.x
    y = loop.y
    d = loop.size / pi
    rx = x-d/2+i
    ry = y-d/2+i
    rw = d-i*2
    rh = d-i*2
    return QRect(rx, ry, rw, rh)

def get_rect_for_item(item, loop, i, item_type=None):
    is_station = isinstance(item, MST.Station)
    # loop
    xl = loop.x
    yl = loop.y
    dl = loop.size / pi
    rl = dl / 2
    if is_station:
        angle = item.angle
    elif item_type == "switch_out":
        angle = item.angle_my_loop
    else:
        angle = item.angle_other_loop
    angle += 90
    angle = angle * 2 * pi / 360
    # center of item
    xi = xl - rl * cos(angle)
    yi = yl - rl * sin(angle)
    # rect
    item = "station" if is_station else "switch"
    item_width = int(config.interface["{0}_width".format(item)])
    item_height = int(config.interface["{0}_height".format(item)])
    xr = xi - item_width/2 + i
    yr = yi - item_height/2 + i
    wr = item_width - i*2
    hr = item_height - i*2
    return QRect(xr, yr, wr, hr)
    
