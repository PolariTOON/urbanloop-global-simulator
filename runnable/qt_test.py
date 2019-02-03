#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QApplication
from qt.main_window import *
from sys import exit, argv

if __name__ == '__main__':
    app = QApplication(argv)
    window = MainWindow(app)
    exit(app.exec_())