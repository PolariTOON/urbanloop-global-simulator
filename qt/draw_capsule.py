#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPicture, QPainter, QColor
from PyQt5.QtCore import Qt, QPoint

from settings import config

"""
draw a simple graphical object representing a capsule
return a clickable QPicture
"""


class CapsuleRenderer:
    def __init__(self, root, capsule, percentage):
        assert root is not None and capsule is not None and percentage is not None and handler != None  # TODO handler
        self.config = config.interface
        self.root = root
        self.capsule = capsule
        self.percentage = percentage
        self.handler = self.root.handler
        # image
        pic = QPicture()
        pic.resize(int(self.config["capsule_width"]), int(self.config["capsule_height"]))
        self.color = config["selected_color"] if self.handler.selected_item == self.capsule else self.config[
            "capsule_color"]

    def paint_event(self, event):
        paint = QPainter()
        paint.begin(self.root.image)
        # optional
        paint.setRenderHint(QPainter.Antialiasing)
        # make a red ellipse
        paint.setBrush(QColor(self.color))
        paint.drawRect(event.rect())
        # then make black border
        # for circle make the ellipse radii match
        radx = 100
        rady = 100
        # draw red circles
        paint.setPen(Qt.red)
        for k in range(125, 220, 10):
            center = QPoint(k, k)
            # optionally fill each circle yellow
            paint.setBrush(Qt.yellow)
            paint.drawEllipse(center, radx, rady)
        paint.end()
