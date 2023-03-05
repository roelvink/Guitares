from PyQt5.QtWidgets import QCheckBox
from PyQt5 import QtCore
import traceback

class CheckBox(QCheckBox):

    def __init__(self, element):
        super().__init__("", element.parent.widget)

        self.element = element

        self.setVisible(True)

        if element.text:
            self.setText(element.text)

        self.stateChanged.connect(self.callback)

        self.set_geometry()

    def set(self):
        group  = self.element.variable_group
        name   = self.element.variable
        val    = self.element.getvar(group, name)
        if val == True:
            self.setChecked = True
        else:
            self.setChecked = False

    def callback(self, state):
        group = self.element.variable_group
        name = self.element.variable
        if state == QtCore.Qt.Checked:
            val = True
        else:
            val = False
        self.element.setvar(group, name, True)
        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(val, self)
                # Update GUI
                self.element.window.update()
        except:
            traceback.print_exc()

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
