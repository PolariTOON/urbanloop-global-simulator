#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from sys import path

from model import loop as ML
from qt.handler import Handler
import qt.draw_capsule

def getResourcePath(resource):
    return "{0}/../resources/img/{1}".format(path[0],resource)

class SimulatorWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.handler = Handler(self)
        self.resize(600,600)
        self.loops = ML.all_loops
        if (self.loops == {}):
            # show picture if nothing loaded
            self.image = QPixmap(getResourcePath("nothing.png"))
        else :
            # build view
            print("network")
            self.image = QPixmap(getResourcePath("nothing.png"))
        
        l = QLabel()
        l.setPixmap(self.image)
        layout = QHBoxLayout(self)
        layout.addWidget(l)

        