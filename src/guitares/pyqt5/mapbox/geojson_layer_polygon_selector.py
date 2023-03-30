from .layer import Layer
from geopandas import GeoDataFrame

class GeoJSONLayerPolygonSelector(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self,
                 data,
                 index = "",
                 hover_property = ""):

        self.data = data
        self.index = index
        self.hover_property = hover_property

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                data = GeoDataFrame()

        # Remove existing layer        
        self.remove()

        # Add new layer        
        self.mapbox.runjs("./js/geojson_layer_polygon_selector.js", "addLayer", arglist=[self.map_id,
                                                                                         data,
                                                                                         index,
                                                                                         hover_property,
                                                                                         self.line_color,
                                                                                         self.line_width,
                                                                                         self.line_opacity,
                                                                                         self.fill_color,
                                                                                         self.fill_opacity,
                                                                                         self.selection_type])

    def set_selected_index(self, index):
        self.index = index
        self.mapbox.runjs("/js/geojson_layer_polygon_selector.js", "setSelectedIndex", arglist=[self.map_id, index])

    def activate(self):
        self.active = True
        self.mapbox.runjs("./js/geojson_layer_polygon_selector.js", "activate", arglist=[self.map_id,
                                                                                         self.line_color,
                                                                                         self.fill_color,
                                                                                         self.line_color_selected,
                                                                                         self.fill_color_selected])
  
    def deactivate(self):
        self.active = False
        self.mapbox.runjs("./js/geojson_layer_circle_selector.js", "deactivate", arglist=[self.map_id,
                                                                                          self.line_color_inactive,
                                                                                          self.line_width_inactive,
                                                                                          self.line_style_inactive,
                                                                                          self.line_opacity_inactive,
                                                                                          self.fill_color_inactive,
                                                                                          self.fill_opacity_inactive,
                                                                                          self.line_color_selected_inactive,
                                                                                          self.fill_color_selected_inactive])

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index, self.hover_property)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        self.remove()

    def remove(self):
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id + ".fill"])
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id + ".line"])
        self.mapbox.runjs("./js/main.js", "removeLayer", arglist=[self.map_id])

    def update(self):
        pass

    def set_visibility(self, true_or_false):
        if true_or_false:
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".fill"])
            self.mapbox.runjs("/js/main.js", "showLayer", arglist=[self.map_id + ".line"])
        else:
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".fill"])
            self.mapbox.runjs("/js/main.js", "hideLayer", arglist=[self.map_id + ".line"])
