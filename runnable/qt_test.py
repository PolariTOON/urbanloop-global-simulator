#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QApplication
import logging
from qt.main_window import *
from sys import exit, argv

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

if __name__ == '__main__':
    app = QApplication(argv)
    window = MainWindow(app)
    exit(app.exec_())
