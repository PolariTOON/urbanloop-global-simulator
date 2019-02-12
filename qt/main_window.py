#! /usr/bin/env python3
# coding: utf-8

import logging
from sys import path
from threading import Thread

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QAction, QFileDialog, QPushButton, QHBoxLayout, \
    QVBoxLayout, QLabel, QSplitter

from qt.data_widget import DataWidget
from qt.simulator_widget import SimulatorWidget
from settings import network
from simulator import sim_loop as sim

window = None


def get_resource_path(resource):
    return "{0}/../resources/img/{1}".format(path[0], resource)


class MainWindow(QMainWindow):
    def __init__(self, root):
        global window
        window = self
        self.speed = 1.
        self.state = "None"
        self.root = root
        QMainWindow.__init__(self)
        self.init_ui()

    def reset_capsules(self):
        self.simulator.reset_capsules()

    def init_ui(self):
        # window itself
        self.root.setWindowIcon(QIcon(get_resource_path("icon.png")))
        # self.resize(1000, 600)
        self.center()
        self.setWindowTitle('URBANLOOP Simulator')

        # menu
        def open_file():
            logging.debug("Custom Network File")
            file_path = self.open_file_name_dialog()
            network.load(file_path)
            self.refresh()
            return

        def open_sample():
            logging.debug("Default Network File")
            network.load()
            self.refresh()
            return

        # buttons
        def on_decrease_button_pressed():
            # speed label
            self.speed /= 2
            self.speed_label.setText(self.speed_label.text().split(" : ")[0] + " : x%f" % self.speed)
            # decrease speed
            sim.decelerate_sim()

        def on_stop_button_pressed():
            # buttons
            self.play_button.setDisabled(False)
            self.stop_button.setDisabled(True)
            self.pause_button.setDisabled(True)
            self.increase_speed_button.setDisabled(True)
            self.decrease_speed_button.setDisabled(True)
            # state label
            self.state = "stopped"
            self.state_label.setText(self.state_label.text().split(" : ")[0] + " : %s" % self.state)
            # stop simulation
            # self.thd = None
            sim.stop_simulation()

        def on_play_button_pressed():
            # buttons
            self.play_button.setDisabled(True)
            self.stop_button.setDisabled(False)
            self.pause_button.setDisabled(False)
            self.increase_speed_button.setDisabled(False)
            self.decrease_speed_button.setDisabled(False)
            # state label
            self.state = "running"
            self.state_label.setText(self.state_label.text().split(" : ")[0] + " : %s" % self.state)
            # starting thread
            self.thd = Thread(target=sim.run_simulation)
            self.thd.start()
            print("thread started")

        def on_pause_button_pressed():
            self.state = "paused"
            self.state_label.setText(self.state_label.text().split(" : ")[0] + " : %s" % self.state)
            self.play_button.setDisabled(False)
            self.pause_button.setDisabled(True)

        def on_increase_button_pressed():
            self.speed *= 2
            self.speed_label.setText(self.speed_label.text().split(" : ")[0] + " : x%f" % self.speed)
            sim.accelerate_sim()

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        open_file_act = QAction('Open file...', self)
        open_file_act.setShortcut('Ctrl+O')
        open_file_act.triggered.connect(open_file)
        file_menu.addAction(open_file_act)
        open_sample_act = QAction('Open sample', self)
        open_sample_act.setShortcut('Ctrl+Shift+O')
        open_file_act.triggered.connect(open_sample)
        file_menu.addAction(open_sample_act)
        # content:
        # HBOX
        # +----------------------------------+
        # | +-----------+ |   VBOX           |
        # | |           | |  +-------------+ |
        # | |           | |  | state       | |
        # | |           | |  | +---------+ | |
        # | | simulator | |  | | buttons | | |
        # | |           | |  | +---------+ | |
        # | | view      | |  | +---------+ | |
        # | |           | |  | | data    | | |
        # | |           | |  | +---------+ | |
        # | +-----------+ |  +-------------+ |
        # +----------------------------------+
        # data
        self.title_label = DataWidget()
        data_vbox = QVBoxLayout()
        data_vbox.addWidget(self.title_label)

        # buttons & layout
        self.decrease_speed_button = QPushButton(QIcon(get_resource_path("minus.png")), "")
        self.decrease_speed_button.released.connect(on_decrease_button_pressed)
        self.stop_button = QPushButton(QIcon(get_resource_path("stop.png")), "")
        self.stop_button.released.connect(on_stop_button_pressed)
        self.play_button = QPushButton(QIcon(get_resource_path("play-button.png")), "")
        self.play_button.released.connect(on_play_button_pressed)
        self.pause_button = QPushButton(QIcon(get_resource_path("pause.png")), "")
        self.pause_button.released.connect(on_pause_button_pressed)
        self.increase_speed_button = QPushButton(QIcon(get_resource_path("plus.png")), "")
        self.increase_speed_button.released.connect(on_increase_button_pressed)
        # turning on/off buttons
        self.play_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.increase_speed_button.setDisabled(True)
        self.decrease_speed_button.setDisabled(True)
        # adding em to the layout
        buttons_hbox = QHBoxLayout()
        buttons_hbox.addWidget(self.decrease_speed_button)
        buttons_hbox.addWidget(self.stop_button)
        buttons_hbox.addWidget(self.play_button)
        buttons_hbox.addWidget(self.pause_button)
        buttons_hbox.addWidget(self.increase_speed_button)

        # state label
        self.state_label = QLabel("State : None")
        self.speed_label = QLabel("Speed : x%f" % self.speed)

        # right part
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.state_label)
        right_layout.addWidget(self.speed_label)
        right_layout.addLayout(buttons_hbox)
        right_layout.addWidget(QSplitter())
        right_layout.addLayout(data_vbox)

        # main layout  #TODO Ne sont pas défninis dans _init
        self.simulator = SimulatorWidget(self.title_label)
        separator = QSplitter()
        separator.setOrientation(Qt.Vertical)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.simulator)
        main_layout.addWidget(separator)
        main_layout.addLayout(right_layout)

        # showing it
        w = QWidget()
        w.setLayout(main_layout)
        self.setCentralWidget(w)
        self.show()

    """center the window on the scren"""

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    """open a file dialog.
    return the selected file's path if it exists,
        else return None"""

    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*)",
                                                   options=options)
        return file_name if file_name else None

    """reset simulation, buttons, information panel
        and load a new simulator view"""

    def refresh(self):
        # print("refreshing")
        self.simulator.refresh()
