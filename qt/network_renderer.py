from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPicture, QPainter, QColor
from PyQt5.QtCore import Qt, QRect
from math import pi, cos, sin

from settings import config
import model.loop as ML
import model.station as MST
import model.switch as MSW
import model.capsule as MC
import logging

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
            r = loop.size / 2 / pi  # TODO r not used
            paint.setBrush(
                QColor(self.config["selected_color"] if self.root.selected_item == loop else self.config["loop_color"]))
            paint.drawEllipse(get_rect_for_loop(loop, 0))
            paint.setBrush(QColor("white"))
            paint.drawEllipse(get_rect_for_loop(loop, int(self.config["loop_outline_width"])))
            # display loop's name
            paint.setBrush(QColor("black"))
            paint.drawText(loop.x-len(name)/2*8, loop.y, name)
            # make stations and switches for after painting loop
            self.fill_loop(loop, paint)
        # join loops between themselves
        self.join_loops(paint)
        # draw capsules
        self.draw_capsules(paint)

    def draw_capsules(self, paint):
        capsules = MC._capsules
        for capsule in capsules:
            rect = get_rect_for_capsule(capsule, 0)
            paint.setBrush(QColor(config.interface["selected_color"] if capsule == self.root.selected_item else config.interface["capsule_color"]))
            paint.drawEllipse(rect)
            

    def fill_loop(self, loop, paint):
        item_nbr = 0
        for obj in loop.objects:
            item_type = obj[0]
            item = obj[1]
            if item is not None:
                is_station = isinstance(item, MST.Station)
                if self.root.selected_item == item:
                    paint.setBrush(QColor(self.config["selected_color"]))
                else:
                    paint.setBrush(QColor(self.config["station_color" if is_station else "switch_color"]))
                paint.drawEllipse(get_rect_for_item(item, loop, 0, None if is_station else item_type))
                paint.setBrush(QColor("white"))
                outline_width = int(self.config["switch_outline_width"]) if isinstance(item, MSW.Switch) else int(
                    self.config["station_outline_width"])
                rect = get_rect_for_item(item, loop, outline_width, None if is_station else item_type)
                paint.drawEllipse(rect)
                paint.drawText(rect.getCoords()[0], rect.getCoords()[1], "{0}".format(item_nbr))
                item_nbr += 1

    def join_loops(self, paint):
        for name in ML.all_loops:
            loop = ML.get_by_name(name)
            for obj in loop.objects:
                if isinstance(obj[1], MSW.Switch):
                    if obj[0]=="switch_out":
                        sw = obj[1]
                        # compute coord of switch in both loop
                        current_loop = sw.my_loop
                        current_loop_r = current_loop.size / 2 / pi
                        current_angle = sw.angle_my_loop + 90
                        current_angle *= 2 * pi / 360 
                        x1 = current_loop.x - cos(current_angle) * current_loop_r
                        y1 = current_loop.y - sin(current_angle) * current_loop_r
                        #
                        other_loop = sw.other_loop
                        other_loop_r = other_loop.size / 2 / pi
                        other_angle = sw.angle_other_loop + 90
                        other_angle *= 2 * pi / 360
                        x2 = other_loop.x - cos(other_angle) * other_loop_r
                        y2 = other_loop.y - sin(other_angle) * other_loop_r
                        # compute slope
                        #slope = (x2 - x1) / (y2 - y1)
                        #upper_slope = 
                        #lower_slope = 
                        # draw 
                        paint.drawLine(x1, y1, x2, y2)                        
        return

def get_rect_for_loop(loop, i):
    """
    return the rect in which @param loop
    will be displayed. @param i represent
    the outline width of the loop
    """
    x = loop.x
    y = loop.y
    d = loop.size / pi
    rx = x - d / 2 + i
    ry = y - d / 2 + i
    rw = d - i * 2
    rh = d - i * 2
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
    xr = xi - item_width / 2 + i
    yr = yi - item_height / 2 + i
    wr = item_width - i * 2
    hr = item_height - i * 2
    return QRect(xr, yr, wr, hr)

def get_rect_for_capsule(capsule, i):
    loop = capsule.loop
    percentage = capsule.get_trip_percentage()
    # compute capsule coords
    lx, ly, lr = loop.x, loop.y, loop.size / 2 / pi
    
    if isinstance(capsule.current_element, MSW.Switch):
        sa = capsule.current_element.angle_my_loop
    else:
        sa = capsule.current_element.angle
    if isinstance(capsule.next_element, MSW.Switch):
        nsa = capsule.next_element.angle_my_loop
    else:
        nsa = capsule.next_element.angle
    if nsa < sa:
        nsa += 360
    ca = (nsa-sa) * percentage  + sa
    ca += 90
    ca = ca * 2 * pi / 360
    cx, cy = lx - lr * cos(ca), ly - lr * sin(ca)
    # compute rectangle coord
    cw = int(config.interface["capsule_width"])
    ch = int(config.interface["capsule_height"])
    
    return QRect(cx-cw/2-i, cy-ch/2-i, cw, ch)
