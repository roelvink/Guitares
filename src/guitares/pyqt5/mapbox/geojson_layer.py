import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class GeoJSONLayer(Layer):
    def __init__(self, mapbox, id, map_id,
                 data=None,
                 file_name=None,
                 select=None,
                 type=None,
                 selection_type="single",
                 fill_color="red",
                 fill_opacity=0.75,
                 line_color="black",
                 line_width=1,
                 circle_radius=5,
                 highlight="",
                 ):
        super().__init__(mapbox, id, map_id)
        self.active = False
        self.type   = "geojson"
        self.subtype = type
        self.select_callback = select

        if fill_color != "transparent":
            fill_color = mcolors.to_hex(fill_color)
        if line_color != "transparent":
            line_color = mcolors.to_hex(line_color)

        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if file_name:
#                xxx = data.to_json()
                with open(os.path.join(self.mapbox.server_path, "overlays", file_name), "w") as f:
                    if "timeseries" in data:
                        f.write(data.drop(columns=["timeseries"]).to_crs(4326).to_json())
                    else:
                        f.write(data.to_crs(4326).to_json())

                data = "./overlays/" + file_name
            else:
                data = data.to_json()
        else:
            data = []
        if type == "polygon_selector":
            self.mapbox.runjs("./js/geojson_layer_polygon_selector.js", "addLayer", arglist=[self.map_id,
                                                                                             data,
                                                                                             fill_color,
                                                                                             fill_opacity,
                                                                                             line_color,
                                                                                             line_width,
                                                                                             selection_type,
                                                                                             highlight])

        elif type == "marker_selector":
            self.mapbox.runjs("./js/geojson_layer_marker_selector.js", "addLayer", arglist=[self.map_id,
                                                                                            data,
                                                                                            fill_color,
                                                                                            fill_opacity,
                                                                                            line_width,
                                                                                            circle_radius,
                                                                                            selection_type,
                                                                                            highlight])
        elif type == "circle":
            self.mapbox.runjs("./js/geojson_layer_circle.js", "addLayer", arglist=[self.map_id,
                                                                                   data,
                                                                                   fill_color,
                                                                                   fill_opacity,
                                                                                   line_color,
                                                                                   line_width,
                                                                                   circle_radius,
                                                                                   selection_type])

        else:
            self.mapbox.runjs("./js/geojson_layer.js", "addLayer", arglist=[self.map_id, data])

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        self.mapbox.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])

    def update(self):
        pass

    def set_data(self,
                 data,
                 legend_title="",
                 crs=None):
        # Make sure this is not an empty GeoDataFrame
        if len(data) > 0:
            self.mapbox.runjs("/js/geojson_layer.js", "setData", arglist=[self.map_id, data])

    def highlight_data(self, column, name):
        self.mapbox.runjs("/js/geojson_layer_polygon_selector.js", "highlightData", arglist=[self.map_id, column, name])

    def set_visibility(self, true_or_false):
        # TODO probably better to have different file for each type of layer?
        if true_or_false:
            if self.subtype == "marker_selector":
                self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id])
            else:
                self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".fill"])
                self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
                if self.subtype != "polygon_selector":
                    self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".circle"])
                else:
                    self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".fill2"])
                    self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line2"])
        else:
            if self.subtype == "marker_selector":
                self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id])
            else:
                self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".fill"])
                self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
                if self.subtype != "polygon_selector":
                    self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".circle"])
                else:
                    self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".fill2"])
                    self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line2"])


