#! /usr/bin/env python3
# coding: utf-8

from PyQt5.QtWidgets import QMainWindow, QWidget, QDesktopWidget, QAction, QFileDialog, QPushButton, QHBoxLayout, \
    QVBoxLayout, QLabel, QTextEdit, QSplitter
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from sys import path

from settings import network
from qt.simulator_widget import SimulatorWidget


def get_resource_path(resource):
    return "{0}/../resources/img/{1}".format(path[0], resource)


class MainWindow(QMainWindow):
    def __init__(self, root):
        self.root = root
        QMainWindow.__init__(self)
        self.init_ui()

    def init_ui(self):
        # window itself
        self.root.setWindowIcon(QIcon(get_resource_path("icon.png")))
        self.resize(1000, 600)
        self.center()
        self.setWindowTitle('URBANLOOP Simulator')

        # menu
        def open_file():
            file_path = self.open_file_name_dialog()
            network.load(file_path)
            self.refresh()
            return

        def open_sample():
            network.load(None)  # load default network
            self.refresh()
            return

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
        # | |           | |  | +---------+ | |
        # | | simulator | |  | | buttons | | |
        # | |           | |  | +---------+ | |
        # | | view      | |  | +---------+ | |
        # | |           | |  | | data    | | |
        # | |           | |  | +---------+ | |
        # | +-----------+ |  +-------------+ |
        # +----------------------------------+
        # data #TODO Ne sont pas défninis dans _init
        self.title_label = QLabel("Nothing selected")
        self.data_textedit = QTextEdit()
        self.data_textedit.setEnabled(False)
        data_vbox = QVBoxLayout()
        data_vbox.addWidget(self.title_label)
        data_vbox.addWidget(self.data_textedit)

        # buttons & layout  #TODO Ne sont pas défninis dans _init
        self.decrease_speed_button = QPushButton(QIcon(get_resource_path("minus.png")), "")
        self.stop_button = QPushButton(QIcon(get_resource_path("stop.png")), "")
        self.play_button = QPushButton(QIcon(get_resource_path("play-button.png")), "")
        self.pause_button = QPushButton(QIcon(get_resource_path("pause.png")), "")
        self.increase_speed_button = QPushButton(QIcon(get_resource_path("plus.png")), "")
        buttons_hbox = QHBoxLayout()
        buttons_hbox.addWidget(self.decrease_speed_button)
        buttons_hbox.addWidget(self.stop_button)
        buttons_hbox.addWidget(self.play_button)
        buttons_hbox.addWidget(self.pause_button)
        buttons_hbox.addWidget(self.increase_speed_button)

        # right part
        right_layout = QVBoxLayout()
        right_layout.addLayout(buttons_hbox)
        right_layout.addWidget(QSplitter())
        right_layout.addLayout(data_vbox)

        # main layout  #TODO Ne sont pas défninis dans _init
        self.simulator = SimulatorWidget()
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
        return
