from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon

from .widget_group import WidgetGroup


class PushButton(WidgetGroup):
    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QPushButton(element["text"], parent)
        self.widgets.append(b)

        x0, y0, wdt, hgt = element["window"].get_position_from_string(element["position"], parent)
        b.setGeometry(x0, y0, wdt, hgt)

        if element["module"]:
            if "method" in element:
                fcn = getattr(element["module"], element["method"])
                b.clicked.connect(fcn)
            else:
                print("No method found in element !")
        if "icon" in element.keys():
            b.setIcon(QIcon(element["icon"]))
        if "tooltip" in element.keys():
            b.setToolTip(element["tooltip"])

    def set(self):
        self.set_dependencies()

    def callback(self):
        # Callback already set
        pass
