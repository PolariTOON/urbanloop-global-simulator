from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton, QLabel, QGridLayout
from settings import config

changed = {}

class ConfigWindows(QWidget):
    def __init__(self, parent=None):
        super(ConfigWindows, self).__init__(parent)

        self.setWindowTitle(u"Configuration")
        self.posit = QGridLayout()
        self.lign = 0

        title = QLabel("CURRENT CONFIGURATION \n "
                       "\t red is for changed parameters from the default configuration \n "
                       "\t '-1' is for 'no limit'  ")

        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1

        # TRAVELERS
        title = QLabel("TRAVELERS")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("travelers per day", config.default['travelers_per_day'])
        self.add_lign("maximum number of trips", config.default['trip_limit'])
        self.add_lign("maximum number of travelers", config.default['traveler_limit'])
        self.add_lign("average time of descent and ascent", config.capsule['ascent_descent_duration'])


        # CAPSULES
        title = QLabel(" \n \t CAPSULES")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("capsules' speed", config.capsule['max_speed'])

        # ROUTING
        title = QLabel(" \n \t ROUTING")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("", config.default['traveler_limit'])
        self.add_lign("cost added if changing loop", config.routing['switched_cost'])
        self.add_lign("timer to send 'alive' message", config.routing['my_timer'])
        self.add_lign("timer to wait news from other switches", config.routing['timer_other'])
        self.add_lign("maximum number of travelers", config.default['traveler_limit'])

        # TOPOLOGY & SIMULATION
        title = QLabel(" \n \t SIMULATOR AND TOPOLOGY")
        self.posit.addWidget(title, self.lign, 0)
        self.lign += 1
        self.add_lign("duration", config.sim['duration'])
        self.add_lign("start hour", config.sim['start_hour'])
        self.add_lign("default network file", config.model['network_file'])

        self.bouton = QPushButton(u"Save", self)
        self.bouton.clicked.connect(self.ok_m)
        self.posit.addWidget(self.bouton, self.lign+2, 2)

        self.change_color()
        self.setLayout(self.posit)

    def change_color(self):
        for i in range(self.posit.count()):
            if type(self.posit.itemAt(i).widget()) is QLineEdit:
                label = self.posit.itemAt(i-1).widget().text()
                fill = self.posit.itemAt(i).widget()
                if label in changed or fill.text() != fill.objectName():
                    fill.setStyleSheet("color: red;")
                    changed[label] = fill.text()

    def add_lign(self, label, value):
        line_label = QLabel(label)
        line_value = QLineEdit()
        line_value.setText(value)
        line_value.setObjectName(line_value.text())
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
            update_config()
        self.close()

def update_config():
    print(changed)
    for label, value in changed.items():
        if label == 'travelers per day':
            config.default['travelers_per_day'] = value
        if label == "maximum number of trips":
            config.default['trip_limit'] = value
        if label == "maximum number of travelers" :
            config.default['traveler_limit'] = value