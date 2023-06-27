import os

import datashader as ds
import datashader.transfer_functions as tf
from datashader.utils import export_image
import spatialpandas as sp
import warnings
import numpy as np
from pyogrio import read_dataframe

from pyproj import CRS, Transformer


from .layer import Layer

class DatashaderChoroplethLayer(Layer):
    def __init__(self, mapbox, id, map_id):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "image"
        self.file_name = map_id + ".png"

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def make_overlay(self):    

        width = self.mapbox.view.geometry().width()
 
        file_name = os.path.join(self.mapbox.server_path, "overlays", self.file_name)

        coords = self.mapbox.map_extent

        xl0 = coords[0][0]
        xl1 = coords[1][0]
        yl0 = coords[0][1]
        yl1 = coords[1][1]
         
        # Limits WGS 84 
        xlim0 = [xl0, xl1]
        ylim0 = [yl0, yl1]

        transformer = Transformer.from_crs(4326,
                                    3857,
                                    always_xy=True)
        xl0, yl0 = transformer.transform(xl0, yl0)
        xl1, yl1 = transformer.transform(xl1, yl1)

        # Limits web mercator 
        xlim = [xl0, xl1]
        ylim = [yl0, yl1]

        ratio = (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
        height = int(width * ratio)

        cvs = ds.Canvas(x_range=xlim, y_range=ylim, plot_height=height, plot_width=width)
        imgs = []
        agg = cvs.polygons(self.data, geometry='geometry', agg=ds.sum('Dmg Total'))
        imgs.append(tf.shade(agg))
        agg = cvs.line(self.data, geometry='geometry', agg=ds.sum('Dmg Total'), line_width=1)
        imgs.append(tf.shade(agg, cmap="black"))
        img = tf.stack(*imgs)

        path = os.path.dirname(file_name)
        name = os.path.basename(file_name)
        name = os.path.splitext(name)[0]
        export_image(img, name, export_path=path)

        return xlim0, ylim0

    def update(self):
        if self.data is None:
            return
        xlim, ylim = self.make_overlay()
        if xlim is None:
            return
        bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
        bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"
        overlay_file = "./overlays/" + self.file_name
        js_string = "import('/js/image_layer.js').then(module => {module.updateLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + ","")});"
        self.mapbox.view.page().runJavaScript(js_string)
        js_string = "import('/js/image_layer.js').then(module => {module.setOpacity('" + self.map_id + "', 1.0)});"
        self.mapbox.view.page().runJavaScript(js_string)

    def set_data(self,
                 data,
                 image_file=None,
                 xlim=None,
                 ylim=None):

        # Remove old layer  
        js_string = "import('/js/main.js').then(module => {module.removeLayer('" + self.map_id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

        if type(data) == str:
            # Read geodataframe from shape file
            self.data = read_dataframe(data)
            self.data.set_crs(4326)
            self.data = self.data.to_crs(3857)
        else:    
            # data has to be geodataframe
            self.data = data

        # Convert to spatialpandas geodataframe
        self.data = sp.GeoDataFrame(self.data)

        try:
            xlim, ylim = self.make_overlay()
            if xlim is None:
                return
        except:
            print("Something went wrong with map overlay : " + self.map_id)
            return
        bounds = [[xlim[0], xlim[1]], [ylim[0], ylim[1]]]
        bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"
        overlay_file = "./overlays/" + self.file_name
        js_string = "import('/js/image_layer.js').then(module => {module.addLayer('" + overlay_file + "','" + self.map_id + "'," + bounds_string + ","")});"
        self.mapbox.view.page().runJavaScript(js_string)