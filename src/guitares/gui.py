import os
import yaml
import importlib
import time
import sched
import sys
import copy
import shutil

from pathlib import Path
import toml
import http.server
import socketserver
from urllib.request import urlopen
from urllib.error import *
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui

from guitares.window import Window

class GUI:
    def __init__(self, module,
                 framework="pyqt5",
                 splash_file=None,
                 stylesheet=None,
                 config_path=None,
                 config_file=None,
                 icon=None,
                 server_path=None,
                 server_port=3000,
                 js_messages=True,
                 copy_mapbox_server_folder=True,
                 mapbox_token_file="mapbox_token.txt"):

        self.module      = module
        self.framework   = framework
        self.splash_file = splash_file
        self.stylesheet  = stylesheet
        self.config_file = config_file
        self.config_path = config_path
        self.splash      = None
        self.icon        = icon
        self.config      = {}
        self.variables   = {}
        self.server_thread = None
        self.server_path = server_path
        self.server_port = server_port
        self.js_messages = js_messages
        self.popup_data = None
        self.resize_factor = 1.0

        if not self.config_path:
            self.config_path = os.getcwd()

        self.image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
        self.image_path = self.image_path.replace(os.sep, '/')

        if server_path:
            # Need to run http server (e.g. for MapBox)
            print("Starting http server ...")
            # Run http server in separate thread
            # Use daemon=True to make sure the server stops after the application is finished
            if copy_mapbox_server_folder:
                mpboxpth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyqt5", "mapbox", "server")
                # Delete current server folder
                if os.path.exists(server_path):
                    shutil.rmtree(server_path)
                # Now copy over folder from mapbox
                shutil.copytree(mpboxpth, server_path)
            thr = threading.Thread(target=run_server, args=(server_path, server_port), daemon=True)
            thr.start()

            # Read mapbox token and store in js file in server path
            if os.path.exists(os.path.join(module.main_path, mapbox_token_file)):
                fid = open(os.path.join(module.main_path, mapbox_token_file), "r")
                mapbox_token = fid.readlines()
                fid.close()
                fid = open(os.path.join(server_path, "mapbox_token.js"), "w")
                fid.write("mapbox_token = '" + mapbox_token[0].strip() + "';")
                fid.close()


    def show_splash(self):
        if self.framework == "pyqt5" and self.splash_file:
            from .pyqt5.splash import Splash
            self.splash = Splash(self.splash_file, seconds=2.0).splash

    def close_splash(self):
        if self.splash:
            self.splash.close()

    def build(self):

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        app = QApplication(sys.argv)

        # Show splash screen
        self.show_splash()

        # Set the icon
        app.setWindowIcon(QtGui.QIcon(self.icon))

        if self.stylesheet:
            app.setStyleSheet(open(os.path.join(self.config_path, self.stylesheet), "r").read())

        if self.config_file:
            self.config = self.read_gui_config(self.config_path, self.config_file)

        # Make window object
        self.window = Window(self.config, self)

        window_widget = self.window.build()

        # Call on_build method after building window
        if hasattr(self.module, "on_build"):
            self.module.on_build()
            
        # Close splash screen before GUI is initiated
        self.close_splash()

        app.exec_()

    def setvar(self, group, name, value):
        if group not in self.variables:
            self.variables[group] = {}
        if name not in self.variables[group]:
            self.variables[group][name] = {}
        self.variables[group][name]["value"] = value

    def getvar(self, group, name):
        if group not in self.variables:
            print("Error! GUI variable group '" + group + "' not defined !")
            return None
        elif name not in self.variables[group]:
            print("Error! GUI variable '" + name + "' not defined in group '" + group + "'!")
            return None
        return self.variables[group][name]["value"]

    def popup(self, config, data=None):
        # Make pop-up window
        # config needs to be file name of yml file, or configuration dict
        # Data is optional and can have any shape (e.g. dict, str, object, etc.)
        # Data will only be changed if Okay is clicked in the pop-up window
        if type(config) == str:
            path = os.path.dirname(config)
            file_name = os.path.basename(config)
            config = self.read_gui_config(path, file_name)
        if data:    
            self.popup_data = copy.copy(data)
        self.popup_window = Window(config, self, type="popup")
        p = self.popup_window.build()
        okay = False
        if p.result() == 1:
            okay = True
            if data:
                data = self.popup_data
        # Only return "data" if it was also entered (otherwise just return True or False (for OK or Cancel, respectively))        
        if data:
            return okay, data
        else:
            return okay

    def read_gui_config(self, path, file_name):
        suffix = Path(path).joinpath(file_name).suffix
        if suffix == '.yml':
            d = yaml2dict(os.path.join(path, file_name))
        elif suffix == '.toml':
            d = toml.load(os.path.join(path, file_name))
        config = {}
        config["window"] = {}
        config["toolbar"] = {}
        config["menu"] = []
        config["element"] = []
        if "window" in d:
            config["window"] = d["window"]
        if "toolbar" in d:
            config["toolbar"] = d["toolbar"]
        if "menu" in d:
            # Recursively read menu
            config["menu"] = d["menu"]
        if "element" in d:
            # Recursively read elements
            config["element"] = self.read_gui_elements(path, file_name)
        return config

    def read_gui_elements(self, path, file_name):
        # Return just the elements
        suffix = Path(path).joinpath(file_name).suffix
        if suffix == '.yml':
            d = yaml2dict(os.path.join(path, file_name))
        elif suffix == '.toml':
            d = toml.load(os.path.join(path, file_name))
        element = d["element"]
        for el in d["element"]:
            if el["style"] == "tabpanel":
                # Loop through tabs
                for tab in el["tab"]:
                    if "element" in tab:
                        if type(tab["element"]) == str:
                            # Must be a file
                            tab["element"] = self.read_gui_elements(path, tab["element"])
                    else:
                        tab["element"] = []
        return element

def yaml2dict(file_name):
    file = open(file_name,"r")
    dct = yaml.load(file, Loader=yaml.FullLoader)
    return dct

def run_server(server_path, server_port):
    os.chdir(server_path)
    PORT = server_port
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map['.js']     = 'text/javascript'
    Handler.extensions_map['.mjs']    = 'text/javascript'
    Handler.extensions_map['.css']    = 'text/css'
    Handler.extensions_map['.html']   = 'text/html'
    Handler.extensions_map['.json']   = 'application/json'
    print("Server path : " + server_path)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()