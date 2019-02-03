#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QPicture

from sys import path
from math import pi, cos, sin

from settings import network, config

from model import loop as ML
from model import switch as MSW
from model import station as MST
from qt.network_renderer import NetworkRenderer
import qt.draw_capsule

config = config.interface

def getResourcePath(resource):
    return "{0}/../resources/img/{1}".format(path[0],resource)

class SimulatorWidget(QWidget):
    def __init__(self):
        network.load()
        self.selected_item = None
        #network.load("{0}/../resources/mini_network_bis.json".format(path[0]))
        QWidget.__init__(self)
        self.resize(600,600) # not working at all
        self.loops = ML.all_loops
        self.simulator_view = QLabel()
        self.refresh() # build image
        layout = QHBoxLayout(self)
        layout.addWidget(self.simulator_view)

    """
    the aim of this is to make clickable the image
    for each represented object, check if click happened
    on it or not; if yes: select it, else unselect
    """
    def select_item(self, event):
        loops = ML.all_loops
        # first compute graphical offsets
        """
        x_offsets = []
        y_offsets = []
        for name in loops:
            loop = ML.get_by_name(name)
            loop_r = loop.size / 2 / pi
            x_offsets.append(loop_r - loop.x)
            y_offsets.append(loop_r - loop.y)
        print(x_offsets, y_offsets)
        x_offset = max(x_offsets)
        y_offset = max(y_offsets)
        """
        # then go
        # 18 and 122 are relative to mini_network.json
        # need to find something better
        x = event.x() - 18# - x_offset
        y = event.y() - 122# - y_offset
        for name in loops:
            loop = ML.get_by_name(name)
            loop_r = loop.size / 2 / pi
            for i in range(len(loop.objects)-1, -1, -1):
                # for each station/switch, starting from last
                # check if click happened on it
                item_type = loop.objects[i][0]
                item = loop.objects[i][1]
                if item_type == "station":
                    item_angle = item.angle
                elif item_type == "switch_in":
                    item_angle = item.angle_other_loop
                else:
                    item_angle = item.angle_my_loop
                item_angle += 90
                item_angle *= 2 * pi / 360
                item_rx = int(config["{0}_width".format(item_type.split("_")[0])])/2
                item_ry = int(config["{0}_height".format(item_type.split("_")[0])])/2
                item_x = loop.x - loop_r * cos(item_angle)
                item_y = loop.y - loop_r * sin(item_angle)
                # computing if click happened inside ellipse or not
                if ((x - item_x)**2/item_rx**2)+((y - item_y)**2/item_ry**2) <= 1:
                    # inside object
                    self.selected_item = item
                    self.refresh()
                    return
                # if you get here, click did not happened on
                # something inside this loop
            # check inside the loop
            if (x - loop.x)**2 + (y - loop.y)**2 <= loop_r**2:
                # click happened inside loop
                self.selected_item = loop
                self.refresh()
                return
        # if we get here, click happened on nothing
        print("unselect")
        self.selected_item = None
        self.refresh()
    
    def refresh(self):
        if (self.loops == {}):
            # show picture if nothing loaded
            self.image = QPixmap(getResourcePath("nothing.png"))
            self.simulator_view.setPixmap(self.image)
        else :
            # build view
            self.image = QPicture()
            nr = NetworkRenderer(self)
            nr.paint()
            self.simulator_view.setPicture(self.image)
            self.simulator_view.mouseReleaseEvent = self.select_item
        return

        