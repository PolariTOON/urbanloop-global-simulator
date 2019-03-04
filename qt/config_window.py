from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton, QLabel, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QFont
from settings import config, simlog
from sys import path

changed = {}
saved = None


class ConfigWindows(QWidget):
    def __init__(self, p, parent=None):
        self.new_changed = {}
        super(ConfigWindows, self).__init__(parent)
        self.main_window = p
        self.setWindowTitle(u"Configuration")
        table = QVBoxLayout()
        space = QLabel()
        space.setText(" ")
        table.addWidget(space)
        t = QLabel(" \t    CURRENT CONFIGURATION \n "
                   "\t \t red is for changed parameters from the default configuration \n "
                   "\t \t '-1' is for 'no limit'  ")
        t.setFont(QFont("Arial", weight=QFont.Bold))
        table.addWidget(t)
        table.addWidget(space)

        self.posit = QGridLayout()
        self.lign = 1
        # TRAVELERS
        title = QLabel("\n \t TRAVELERS")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("travelers per day", config.default['travelers_per_day'], 'travelers_per_day')
        self.add_lign("number of capsules in the network", config.default['number_of_capsules'], 'number_of_capsules')
        self.add_lign("maximum number of trips", config.default['trip_limit'], 'trip_limit')
        self.add_lign("maximum number of travelers", config.default['traveler_limit'], 'traveler_limit')
        self.add_lign("average time of descent and ascent", config.capsule['ascent_descent_duration'], 'ascent_descent_duration')


        # CAPSULES
        title = QLabel(" \n \t CAPSULES")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("capsules' speed", config.capsule['max_speed'], 'max_speed')

        # ROUTING
        title = QLabel(" \n \t ROUTING")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("cost added if changing station", config.routing['switched_cost'], 'switched_cost')
        self.add_lign("timer to send 'alive' message", config.routing['my_timer'], 'my_timer')
        self.add_lign("timer to wait news from other switches", config.routing['timer_other'], 'timer_other')
        self.add_lign("maximum number of travelers", config.default['traveler_limit'], 'traveler_limit')

        # TOPOLOGY & SIMULATION
        title = QLabel(" \n \t SIMULATOR AND TOPOLOGY")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("duration", config.sim['duration'], 'duration')
        self.add_lign("start hour", config.sim['start_hour'], 'start_hour')
        self.add_lign("default network file", config.model['network_file'], 'network_file')

        self.change_color()
        table.addLayout(self.posit)
        table.addWidget(space)

        self.bouton = QPushButton(u"Save", self)
        self.bouton.clicked.connect(self.ok_m)
        table.addWidget(self.bouton)

        table.addWidget(space)
        table.addWidget(space)
        self.setLayout(table)

    def change_color(self):
        for i in range(self.posit.count()):
            if type(self.posit.itemAt(i).widget()) is QLineEdit:
                label = self.posit.itemAt(i-1).widget().objectName()
                fill = self.posit.itemAt(i).widget()
                default_value = fill.objectName()
                if label in changed or label in self.new_changed or fill.text() != default_value:
                    fill.setStyleSheet("color: red;")
                    self.new_changed[label] = fill.text()

    def add_lign(self, label, value, config_label):
        line_label = QLabel(label)
        line_label.setObjectName(config_label)
        line_value = QLineEdit()
        line_value.setText(value)
        line_value.setObjectName(value)
        line_value.textChanged.connect(self.change_color)
        self.posit.addWidget(line_label, self.lign, 0)
        self.posit.addWidget(line_value, self.lign, 1)
        self.lign += 1

    def ok_m(self):
        self.close()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, u"Request to close",
                                     u"Do you want to save the changes and restart the simulation ?",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            global changed
            for label, value in self.new_changed.items():
                changed[label] = value
            update_config()
            self.main_window.stop_button.click()
        else:
            simlog.info("Configuration changements canceled")
        self.close()


def update_config():
    default = "{0}/../resources/default_config.ini".format(path[0])
    config_file = "{0}/../resources/config.ini".format(path[0])
    fs = open(default, 'r')
    fd = open(config_file, 'w')
    for line in fs:
        label = line.split(" = ")[0]
        if label in changed :
            fd.write(label + " = " + changed[label] + "\n")
        else:
            fd.write(line)
    fd.close()
    fs.close()
    simlog.info("Configuration was changed")
    config.load(config_file)