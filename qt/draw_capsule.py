#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPicture
from settings import config

config = config.interface

"""
draw a simple graphical object representing a capsule
return a clickable QPicture
"""
def draw_capsule(root, capsule, percentage, handler):
    assert root != None and capsule != None and percentage != None and handler != None
    w = QPicture()
    w.resize(int(config["capsule_width"]), int(config["capsule_height"]))

    return