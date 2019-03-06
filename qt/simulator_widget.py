from math import pi, cos, sin
from sys import path

from PyQt5.QtGui import QPixmap, QPicture
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from model import loop as ML
from model import capsule as MC
from qt.network_renderer import NetworkRenderer, get_capsule_coordinates
from settings import network, config, simlog

config = config.interface


def get_resource_path(resource):
    """
    Return resource path
    """
    return "{0}/../resources/img/{1}".format(path[0], resource)


class SimulatorWidget(QWidget):
    def __init__(self, data_widget):
        """
        SimulatorWidget constructor
        @param:data_widget if the widget where setData of the self.selected_item is displayed
        """
        self.data_widget = data_widget
        # at start, nothing is selectedObject
        self.selected_item = None
        # creating widget
        QWidget.__init__(self)
        self.loops = ML.all_loops
        self.simulator_view = QLabel()
        self.refresh()  # build image
        layout = QHBoxLayout(self)
        layout.addWidget(self.simulator_view)

    def reset_capsules(self):
        """
        Reset Simulator knowledge of capsules in the network and updateData simulator view
        """
        self.capsules = []
        self.refresh()

    def select_item(self, event):
        """
        Update self.selected_item
        """
        loops = ML.all_loops
        # WARNING
        # this sucks. this is why we must move on another way to display the network
        """
        # first compute graphical offsets
        x_offsets = []
        y_offsets = []
        for name in loops:
            station = model_loop.get_by_name(name)
            loop_r = station.size / 2 / pi
            x_offsets.append(loop_r - station.x)
            y_offsets.append(loop_r - station.y)
        print(x_offsets, y_offsets)
        x_offset = max(x_offsets)
        y_offset = max(y_offsets)
        """
        simlog.debug("click at [{0};{1}]".format(event.x(), event.y()))
        # WARNING
        # relative offsets to old_mini_network.json
        x = event.x() - 18  # - x_offset
        y = event.y() - 102 # - y_offset
        # computing if click happened on a capsule
        for capsule in MC._capsules:
            [cx,cy] = get_capsule_coordinates(capsule)
            rx = int(config["capsule_width"])
            ry = int(config["capsule_height"])
            if (x - cx)**2 / rx**2 + (y - cy)**2 / ry**2 <= 1:
                self.selected_item = capsule
                self.data_widget.refresh(capsule)
                self.refresh()
                return
        for name in loops:
            loop = ML.get_by_name(name)
            loop_r = loop.size / 2 / pi
            for i in range(len(loop.objects) - 1, -1, -1):
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
                item_rx = int(config["{0}_width".format(item_type.split("_")[0])]) / 2
                item_ry = int(config["{0}_height".format(item_type.split("_")[0])]) / 2
                item_x = loop.x - loop_r * cos(item_angle)
                item_y = loop.y - loop_r * sin(item_angle)
                # computing if click happened on a switch or a station
                if (x - item_x) ** 2 / item_rx ** 2 + (y - item_y) ** 2 / item_ry ** 2 <= 1:
                    self.selected_item = item
                    self.data_widget.refresh(item)
                    self.refresh()
                    return
                # if you get here, click did not happened on something on this station
            # computing if click happened inside a station
            if (x - loop.x) ** 2 + (y - loop.y) ** 2 <= loop_r ** 2:
                # click happened inside station
                self.selected_item = loop
                self.data_widget.refresh(loop)
                self.refresh()
                return
        # if we get here, click happened on nothing
        self.selected_item = None
        self.data_widget.refresh(None)
        self.refresh()

    def refresh(self, record=None):
        """
        Refresh simulator view
        """
        self.loops = ML.all_loops
        if self.loops == {}:
            # show picture if nothing loaded
            self.image = QPixmap(get_resource_path("nothing.png"))
            self.simulator_view.setPixmap(self.image)
        else:
            # build view
            self.image = QPicture()  # TODO attribut pas dnas le _init
            nr = NetworkRenderer(self, record)
            nr.paint()
            self.simulator_view.setPicture(self.image)
            self.simulator_view.mouseReleaseEvent = self.select_item
