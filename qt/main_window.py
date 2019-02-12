#! /usr/bin/env python3
# coding: utf-8

import logging
from sys import path
from threading import Thread
from time import sleep, time
from math import ceil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QAction, QFileDialog, QPushButton, QHBoxLayout, \
    QVBoxLayout, QLabel, QSplitter

from qt.data_widget import DataWidget
from qt.simulator_widget import SimulatorWidget
from settings import network, config
from simulator import sim_loop as sim
from model import sim_record

window = None
config = config.sim

#to be removed
network.load()
#to be removed

def get_image_path(image):
    """
    Return image path
    """
    return "{0}/../resources/img/{1}".format(path[0], image)


class MainWindow(QMainWindow):
    def __init__(self, root):
        """
        MainWindow constructor
        """
        global window
        window = self
        self.speed = 1.
        self.state = "None"
        self.root = root
        self.thd_run = None
        self.path = None
        QMainWindow.__init__(self)
        self.refresh_time = float(config["tick"])
        self.init_ui()

    def reset_capsules(self):
        """
        Reset capsules in the network
        """
        self.simulator.reset_capsules()

    def init_ui(self):
        """
        Build UI
        """
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

        # window itself
        self.root.setWindowIcon(QIcon(get_image_path("icon.png")))
        self.center()
        self.setWindowTitle('URBANLOOP Simulator')
        self.build_menu()

        right_layout = self.build_right_part()
        main_layout = self.put_all_together(right_layout)
        self.display(main_layout)

    def center(self):
        """
        Center the window on the screen
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def build_menu(self):
        """
        Build menu on UI
        """
        def open_file():
            """
            Method called when menu button "Open" is pressed
            """
            logging.debug("Using custom network file")
            file_path = self.open_file_name_dialog()
            network.load(file_path)
            self.refresh()

        def open_sample():
            """
            Method called when menu button "Open sample" is pressed
            """
            logging.debug("Using default network file")
            network.load(None)
            self.refresh()
        
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

    def open_file_name_dialog(self):
        """
        Open a file dialog.
        Return the selected file's path if it exists, else return None
        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "QFileDialog.getOpenFileName()", "", "All Files (*)", options=options)
        self.path = file_name if file_name else None
        return self.path

    def build_buttons(self):
        """
        Build buttons from right top hand corner panel
        Return buttons layout
        """
        # button methods
        def on_decrease_button_pressed():
            """
            Method called when button "Decrease" is pressed
            """
            self.speed /= 2
            self.speed_label.setText(self.speed_label.text().split(" : ")[0] + " : x%f" % self.speed)
            # decrease speed
            sim.decelerate_sim()

        def on_stop_button_pressed():
            """
            Method called when menu button "Stop" is pressed
            """
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
            sim.quit_endless_simulation()
            self.thd_run = None
            self.thd_refresh = None
            network.reload(self.path)

        def on_play_button_pressed():
            """
            Method called when menu button "Play" is pressed
            """
            # buttons
            self.play_button.setDisabled(True)
            self.stop_button.setDisabled(False)
            self.pause_button.setDisabled(False)
            self.increase_speed_button.setDisabled(False)
            self.decrease_speed_button.setDisabled(False)
            # state label
            self.state = "running"
            self.state_label.setText(self.state_label.text().split(" : ")[0] + " : %s" % self.state)
            # start or resume simulation
            if self.thd_run == None:
                self.thd_run = Thread(target=sim.run_simulation)
                self.thd_run.start()
                sleep(1)
            
            self.thd_refresh = Thread(target=self.start_refresh)
            self.thd_refresh.start()

        def on_pause_button_pressed():
            """
            Method called when menu button "Pause" is pressed
            """
            self.state = "paused"
            self.state_label.setText(self.state_label.text().split(" : ")[0] + " : %s" % self.state)
            self.play_button.setDisabled(False)
            self.pause_button.setDisabled(True)

        def on_increase_button_pressed():
            """
            Method called when menu button "increase" is pressed
            """
            self.speed *= 2
            self.speed_label.setText(self.speed_label.text().split(" : ")[0] + " : x%f" % self.speed)
            sim.accelerate_sim()
        
        self.decrease_speed_button = QPushButton(QIcon(get_image_path("minus.png")), "")
        self.decrease_speed_button.released.connect(on_decrease_button_pressed)
        self.stop_button = QPushButton(QIcon(get_image_path("stop.png")), "")
        self.stop_button.released.connect(on_stop_button_pressed)
        self.play_button = QPushButton(QIcon(get_image_path("play-button.png")), "")
        self.play_button.released.connect(on_play_button_pressed)
        self.pause_button = QPushButton(QIcon(get_image_path("pause.png")), "")
        self.pause_button.released.connect(on_pause_button_pressed)
        self.increase_speed_button = QPushButton(QIcon(get_image_path("plus.png")), "")
        self.increase_speed_button.released.connect(on_increase_button_pressed)
        # turning on/off buttons
        self.play_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.increase_speed_button.setDisabled(True)
        self.decrease_speed_button.setDisabled(True)
        # adding buttons to the layout
        buttons_hbox = QHBoxLayout()
        buttons_hbox.addWidget(self.decrease_speed_button)
        buttons_hbox.addWidget(self.stop_button)
        buttons_hbox.addWidget(self.play_button)
        buttons_hbox.addWidget(self.pause_button)
        buttons_hbox.addWidget(self.increase_speed_button)
        return buttons_hbox

    def build_right_part(self):
        """
        Build the right part of the window (buttons & information panel)
        Return the corresponding layout
        """
        buttons_hbox = self.build_buttons()
        # data
        self.title_label = DataWidget()
        data_vbox = QVBoxLayout()
        data_vbox.addWidget(self.title_label)
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
        return right_layout

    def put_all_together(self, right_layout):
        """
        Put in an horizontal box the simulator view, a seperator and the right panel
        Return the corresponding layout
        """
        self.simulator = SimulatorWidget(self.title_label)
        separator = QSplitter()
        separator.setOrientation(Qt.Vertical)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.simulator)
        main_layout.addWidget(separator)
        main_layout.addLayout(right_layout)
        return main_layout

    def display(self, layout):
        """
        Display the window
        """
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()

    def refresh(self, record=None):
        """
        Reset simulation, buttons, information panel and load a new simulator view
        """
        self.simulator.refresh(record)

    def start_refresh(self):
        while self.state == "running":
            start = time()
            rec = sim_record.get_record()
            self.refresh(rec)
            end = time()
            logging.debug("Execution time: %f secs" % (end - start))
            # if refresh has taken too much time
            if end - start >= self.refresh_time:
                ticks = ceil((end - start) % self.refresh_time)
                logging.warning("Skipping {0} ticks.".format(ticks))
                for i in range(0, ticks):
                    sim_record.get_record()
                return
            sleep(self.refresh_time)
