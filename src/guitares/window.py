from PyQt5.QtWidgets import QWidget, QVBoxLayout
import importlib

from guitares.element import Element
from guitares.menu import Menu

class MenuBar:
    def __init__(self):
        self.parent = None
        self.widget = None

class Window:
    def __init__(self, config_dict, gui, type="main", data=None):
        self.type   = type
        self.gui    = gui
        self.data   = data
        self.width  = 800
        self.height = 600
        self.title  = ""
        self.module = None
        self.variable_group = "_main"
        self.module = None
        self.icon   = None
        self.modal  = False
        if "width" in config_dict["window"]:
            self.width = config_dict["window"]["width"]
        if "height" in config_dict["window"]:
            self.height = config_dict["window"]["height"]
        if "title" in config_dict["window"]:
            self.title = config_dict["window"]["title"]
        if "module" in config_dict["window"]:
            self.module = importlib.import_module(config_dict["window"]["module"])
        if "variable_group" in config_dict["window"]:
            self.variable_group = config_dict["window"]["variable_group"]
        if "icon" in config_dict["window"]:
            self.module = config_dict["window"]["icon"]
        if "modal" in config_dict["window"]:
            self.modal = config_dict["window"]["modal"]
        self.elements = []
        self.menus    = []
        self.toolbar  = []

        if self.type == "popup":
            # Add OK and Cancel elements
            cancel = {'style': 'pushbutton', 'text': 'Cancel',
                      'position': {'x': -80, 'y': 10, 'width': 50, 'height': 20}, 'method': self.cancel,
                      'dependency': [], 'enable': True}
            ok = {'style': 'pushbutton', 'text': 'OK', 'position': {'x': -20, 'y': 10, 'width': 50, 'height': 20},
                  'method': self.ok, 'dependency': [], 'enable': True}
            config_dict["element"].append(cancel)
            config_dict["element"].append(ok)

        self.add_elements_to_tree(config_dict["element"], self, self)
        self.add_menu_to_tree(self.menus, config_dict["menu"], self)

    def add_elements_to_tree(self, dcts, parent, window):
        parent.elements = []
        for dct in dcts:
            element = Element(dct, parent, window)
            if element.style == "tabpanel":
                for itab, tab_dct in enumerate(dct["tab"]):
                    if "element" in tab_dct:
                        self.add_elements_to_tree(tab_dct["element"],
                                                  element.tabs[itab],
                                                  window)
            elif dct["style"] == "panel":
                if "element" in dct:
                    self.add_elements_to_tree(dct["element"],
                                              element,
                                              window)
            parent.elements.append(element)

    def add_menu_to_tree(self, menu_list, dcts, parent):
        for dct in dcts:
            menu = Menu(dct, parent)
            if "menu" in dct:
                self.add_menu_to_tree(menu.menus, dct["menu"], menu)
            menu_list.append(menu)

    def build(self):

        if self.type=="main":

            # Add main window

            if self.gui.framework=="pyqt5":
                from .pyqt5.main_window import MainWindow
            window = MainWindow(self)

            # Add menu
            menu_bar = MenuBar()
            if self.gui.framework=="pyqt5":
                menu_bar.widget = window.menuBar()
            self.add_menus(self.menus, menu_bar, self.gui)

            # Add toolbar
            # TODO

            # Status bar
            # self.window.statusBar().showMessage('Message in statusbar.')

            # Central widget
            central_widget = QWidget()
            layout = QVBoxLayout()
            central_widget.setLayout(layout)
            window.setCentralWidget(central_widget)
            self.widget = central_widget

        else:

            # Add pop-up window

            if self.gui.framework=="pyqt5":
                from .pyqt5.popup_window import PopupWindow
                window = PopupWindow(self)
            self.widget = window

        # Add elements
        self.add_elements(self.elements)

        # Set elements
        self.update()

        window.show()

        if self.type == "popup":
            window.exec_()

        return window

    def ok(self, *args):
        self.widget.done(1)

    def cancel(self, *args):
        self.widget.done(0)

    def closeEvent(self, event):
        pass

    def update(self):
        # Update all elements
        self.set_elements(self.elements)
        self.set_menus(self.menus)

    def add_elements(self, elements):
        # Loop through elements list
        for element in elements:
            if element.style == "tabpanel":
                # Add tab panel
                element.add()
                # Loop through tabs in tab panel
                for tab in element.tabs:
                    # And now add the elements in this tab
                    if tab.elements:
                        self.add_elements(tab.elements)
            elif element.style == "panel":
                # Add panel
                element.add()
                # And now add the elements in this frame
                if element.elements:
                    self.add_elements(element.elements)
            else:
                element.add()

    def set_elements(self, elements):
        # Loop through elements list
        for element in elements:
            try:
                if element.visible:
                    if element.style == "tabpanel":
                        # Only update the elements in the active tab
                        index = element.widget.currentIndex()
                        # Loop through elements in tab
                        for j, tab in enumerate(element.tabs):
                            # Check if tab has elements
                            if tab.elements and j==index:
                                # And now add the elements in this tab
                                self.set_elements(tab.elements)
                    elif element.style == "panel":
                        # Check if this frame has elements
                        if element.elements:
                            # Set elements in this frame
                            self.set_elements(element.elements)
                    else:
                        # Set the element values
                        element.widget.set()
                        # Set the dependencies
                        element.set_dependencies()
            except Exception as err:
                print(err)

    def find_element_by_id(self, elements, element_id):
        element_found = None
        for element in elements:
            if element.id == element_id:
                return element
            if element.style == "tabpanel":
                # Loop through tabs
                for tab in element.tabs:
                    # Look for elements in this tab
                    if tab.elements:
                        element_found = self.find_element_by_id(tab.elements, element_id)
                        if element_found:
                            return element_found
            elif element.style == "panel":
                # Look for elements in this frame
                if element.elements:
                    element_found = self.find_element_by_id(element.elements, element_id)
                    if element_found:
                        return element_found
        return None

    def resize_elements(self, elements, resize_factor):
        # Loop through elements
        for element in elements:
            # Set geometry of this element
            element.set_geometry()
            if element.style == "tabpanel":
                # Loop through tabs
                for tab in element.tabs:
                    # # Resize tab widgets
                    # tab.widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))
                    # And resize elements in this tab
                    if tab.elements:
                        self.resize_elements(tab.elements, resize_factor)
            elif element.style == "panel":
                # If this panel is resizable, also update element positions of children
                if element.position.height < 0:
                    self.resize_elements(element.elements, resize_factor)

    def add_menus(self, menus, parent, gui):
        # Loop through elements list
        for menu in menus:
            menu.parent = parent
            menu.gui = gui
            menu.add()
            if menu.menus:
                self.add_menus(menu.menus, menu, gui)

    def set_menus(self, menus):
        for menu in menus:
            if menu.menus:
                self.set_menus(menu.menus)
            else:
                menu.set_dependencies()

    def find_menu_item_by_id(self, menu_id, menus=None):
        if menus == None:
            menus = self.menus
        for menu in menus:
            if menu.id == menu_id:
                return menu
            item = self.find_menu_item_by_id(menu_id, menus=menu.menus)
            if item:
                return item
        return None