from PyQt5.QtGui import QPainter, QColor
from math import pi, cos, sin

from PyQt5.QtCore import QRect, QLine
from PyQt5.QtGui import QPainter, QColor

import model.capsule as MC
import model.loop as ML
import model.station as MST
import model.switch as MSW
from settings import config, simlog

config = config.interface

class NetworkRenderer:
    def __init__(self, root, record=None):
        """
        NetworkRenderer constructor
        It is used to draw the network
        """
        self.root = root
        self.outline_width = int(config["loop_outline_width"])
        self.record = record

    def paint(self):
        """
        Draw the network on self.root.image
        """
        paint = QPainter()
        paint.begin(self.root.image)
        paint.setRenderHint(QPainter.Antialiasing)
        for name in ML.all_loops:
            loop = self.draw_loop(name, paint) # draw every loop
            self.fill_loop(loop, paint) # and fill it
        join_loops(paint) # them join loops between themselves
        self.draw_capsules(paint) # finally draw capsules
        # draw frame
        self.draw_frame(paint)
    
    def draw_loop(self, name, paint):
        """
        Draw an empty loop and its name with @param:paint
        """
        loop = ML.get_by_name(name)
        paint.setBrush(
            QColor(config["selected_color"] if self.root.selected_item == loop else config["loop_color"]))
        paint.drawEllipse(get_rect_for_loop(loop, 0))
        paint.setBrush(QColor("white"))
        paint.drawEllipse(get_rect_for_loop(loop, int(config["loop_outline_width"])))
        # display loop's name
        paint.setBrush(QColor("black"))
        paint.drawText(loop.x - len(name) / 2 * 8, loop.y, name)
        return loop

    def fill_loop(self, loop, paint):
        """
        Draw every switch and station which belong to @param:loop with @param;paint
        """
        if self.record != None:
            self.modify_loop(loop, paint)
        for item_descriptor in loop.objects:
            item_type = item_descriptor[0]
            item = item_descriptor[1]
            if item is not None:
                is_station = isinstance(item, MST.Station)
                if self.root.selected_item == item:
                    paint.setBrush(QColor(config["selected_color"]))
                else:
                    paint.setBrush(QColor(config["station_color" if is_station else "switch_color"]))
                paint.drawEllipse(get_rect_for_item(item, loop, 0, None if is_station else item_type))
                paint.setBrush(QColor("white"))
                outline_width = int(config["switch_outline_width"]) if isinstance(item, MSW.Switch) else int(
                    config["station_outline_width"])
                rect = get_rect_for_item(item, loop, outline_width, None if is_station else item_type)
                paint.drawEllipse(rect)
                # update number of capsules
                if is_station:
                    station_pos = get_station_coordinates(item)
                    a = item.angle + 90
                    a *= 2 * pi / 360
                    offset = int(config["station_width"]) / 1.3
                    tx = int(station_pos[0] + offset * cos(a))
                    ty = int(station_pos[1] + offset * sin(a))
                    paint.drawText(tx, ty, "{0}".format(len(item.capsule_queue.queue)))

    def modify_loop(self, loop, paint):
        """
        Update stations information only. Called when showing from a record
        """
        for station in self.record.stations:
            if station.loop == loop:
                for item_descriptor in loop.objects:
                    item = item_descriptor[1]
                    if isinstance(item, MST.Station):
                        if station.id == item.id:
                            # update setData
                            item.traveler_queue = station.traveler_queue
                            item.capsule_queue = station.capsule_queue

    def draw_capsules(self, paint):
        """
        Draw capsules with @param:paint
        """
        capsules = MC.get_capsules() if self.record == None else self.record.capsules
        for capsule in capsules:
            rect = get_rect_for_capsule(capsule, 0)
            if capsule == self.root.selected_item:
                color = config["selected_color"]
            else:
                color = config["capsule_color_empty"] if len(capsule.travelers) == 0 else config["capsule_color_full"]
            paint.setBrush(QColor(color))
            paint.drawEllipse(rect)

    def draw_frame(self, paint):
        """
        Draw frame around the simulator view with @param:paint
        """
        x,y = float('inf'), float('inf')
        loop_x, loop_y = None, None
        for ln in ML.all_loops:
            l=ML.get_by_name(ln)
            if l.x < x:
                x = l.x
                loop_x = l
            if l.y < y:
                y = l.y
                loop_y = l
        x-= loop_x.size / 2 / pi
        y-= loop_y.size / 2 / pi
        offset_x = int(config["station_width"]) * 0.75
        offset_y = int(config["station_height"]) * 0.75
        x-= offset_x
        y-= offset_y
        img_width = self.root.image.width() + offset_x
        img_height = self.root.image.height() + offset_y
        color = QColor("blue")
        color.setAlpha(1)
        paint.setBrush(color)
        paint.drawRect(x, y, img_width, img_height)

def join_loops(paint):
    """
    Draw a line between every switch_in and its associated switch_out with @param:paint
    """
    for name in ML.all_loops:
        loop = ML.get_by_name(name)
        for obj in loop.objects:
            if isinstance(obj[1], MSW.Switch):
                if obj[0] == "switch_out":
                    sw = obj[1]
                    line = get_line_for_switch(sw)
                    paint.drawLine(line)

def get_rect_for_loop(loop, i):
    """
    Return the rect in which @param loop will be displayed
    @param i is an absolute offset
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
    """
    Return the rect in which @param:item will be displayed, relatively the the @param:loop
    @param:i is an absolute offset
    @param:item_type is useful for switches (_out or _in)
    """
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
    item_width = int(config["{0}_width".format(item)])
    item_height = int(config["{0}_height".format(item)])
    xr = xi - item_width / 2 + i
    yr = yi - item_height / 2 + i
    wr = item_width - i * 2
    hr = item_height - i * 2
    return QRect(xr, yr, wr, hr)

def get_rect_for_capsule(capsule, i):
    """
    Return the rect in which @param:capsule will be displayed
    @param:i is an absolute offset
    """
    [cx,cy] = get_capsule_coordinates(capsule)
    # compute rectangle coord
    cw = int(config["capsule_width"])
    ch = int(config["capsule_height"])

    return QRect(cx - cw / 2 - i, cy - ch / 2 - i, cw, ch)

def get_line_for_switch(switch):
    """
    Return the QLine to join two loops between @param:switch in/out
    """
    # first loop
    r = switch.my_loop.size / 2 / pi
    a = switch.angle_my_loop + 90
    a *= 2 * pi / 360
    x1 = switch.my_loop.x - cos(a) * r
    y1 = switch.my_loop.y - sin(a) * r
    # second loop
    r = switch.other_loop.size / 2 / pi
    a = switch.angle_other_loop + 90
    a *= 2 * pi / 360
    x2 = switch.other_loop.x - cos(a) * r
    y2 = switch.other_loop.y - sin(a) * r
    return QLine(x1, y1, x2, y2)

def get_capsule_coordinates(capsule):
    """
    Return @param:capsule's coordinates
    """
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
    ca = (nsa - sa) * percentage + sa
    ca += 90
    ca = ca * 2 * pi / 360
    cx, cy = lx - lr * cos(ca), ly - lr * sin(ca)
    return [cx,cy]

def get_station_coordinates(station):
    """
    Return @param:station's coordinates
    """
    l = station.loop
    lr = l.size / 2 / pi
    a = station.angle + 90
    a = a * 2 * pi / 360
    sx, sy = l.x - lr * cos(a), l.y - lr * sin(a)
    return [sx, sy]
