# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:40:07 2022

@author: ormondt
"""
import os

from guitools.gui import GUI


class VisualDelta:
    def __init__(self):
#        gui_module = __import__(__name__)

        self.main_path = os.path.dirname(os.path.abspath(__file__))

#        path = os.path.abspath(__file__)
#        dir_path = os.path.dirname(path)
        server_path = os.path.join(self.main_path, "server")
        self.server_path = server_path

        self.gui = GUI(self,
                       framework="pyqt5",
                       splash_file="visualdelta.jpg",
                       config_file="visualdelta.yml",
                       stylesheet="Combinear.qss",
                       config_path=self.main_path,
                       server_path=server_path,
                       server_port=3000)


    def initialize(self):

        # Define variables
        self.ssp        = 245
        self.impact     = "Flooding"
        self.exposure   = "Population"
        self.adaptation = "Floodwall"
        self.year       = 2022
        self.slr        = 0.0

        # Define GUI variables
        self.gui.setvar("visualdelta", "ssp", self.ssp)
        self.gui.setvar("visualdelta", "ssp_values", [119, 126, 245, 370, 585])
        self.gui.setvar("visualdelta", "ssp_strings", ["SSP1-1.9", "SSP1-2.6", "SSP2-4.5", "SSP3-7.0", "SSP5-8.5"])
        self.gui.setvar("visualdelta", "impact", self.impact)
        self.gui.setvar("visualdelta", "impact_values", ["Flooding", "Erosion", "Salt Intrusion", "Drought", "Other..."])
        self.gui.setvar("visualdelta", "impact_strings", ["Flooding", "Erosion", "Salt Intrusion", "Drought", "Other..."])
        self.gui.setvar("visualdelta", "exposure", self.exposure)
        self.gui.setvar("visualdelta", "exposure_values", ["Population", "Transport", "Critical Infrastructure", "Economy", "Other..."])
        self.gui.setvar("visualdelta", "exposure_strings", ["Population", "Transport", "Critical Infrastructure", "Economy", "Other..."])
        self.gui.setvar("visualdelta", "adaptation", self.adaptation)
        self.gui.setvar("visualdelta", "adaptation_text", "Floodwall")
        self.gui.setvar("visualdelta", "year", self.year)
        self.gui.setvar("visualdelta", "slr", self.slr)
        self.gui.setvar("visualdelta", "slr_string", "{} m ({} - {} m)".format(0.,0.,0.))

#        self.main_path = os.path.dirname(os.path.abspath(__file__))



visualdelta = VisualDelta()
