from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QTextEdit, QVBoxLayout

from model.loop import Loop
from model.switch import Switch
from model.station import Station
from model.capsule import Capsule


class DataWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        '''self.title_label = DataWidget()  # QLabel("Nothing selected")
                        # self.data_textedit = QTextEdit()
                        # self.data_textedit.setEnabled(False)
                        data_vbox = QVBoxLayout()
                        data_vbox.addWidget(self.title_label)
                        # data_vbox.addWidget(self.data_textedit)'''
        self.title = QLabel("Nothing selected")
        self.data_textedit = QTextEdit()
        self.data_textedit.setEnabled(False)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.data_textedit)

    def refresh(self, item):
        if item is not None:
            item_type = type(item)
            if item_type is Loop:
                self.title.setText("Loop " + item.name)
            elif item_type is Station:
                self.title.setText("Station " + item.name)
            elif item_type is Switch:
                self.title.setText("Switch " + str(item.id))
            elif item_type is Capsule:
                self.title.setText("Capsule " + str(item.id))
            self.data_textedit.setText(item.show_details())
        # self.layout = QHBoxLayout(self)
        else :
            self.title.setText("Nothing selected")
            self.data_textedit.setText()
        self.layout.update()
        return