from ra2ceGUI import Ra2ceGUI
from src.guitools.pyqt5.io import openFileNameDialog

import numpy as np
from pathlib import Path


def selectRoad():
    coords = Ra2ceGUI.gui.getvar("ra2ceGUI", "coords_clicked")

    # Remove the marker from the map after the road has been selected

    Ra2ceGUI.edited_flood_depth = Ra2ceGUI.gui.getvar("ra2ceGUI", "edited_flood_depth")
    print(f'Flood depth input: {Ra2ceGUI.edited_flood_depth}')

    try:
        assert Ra2ceGUI.ra2ceHandler
    except AssertionError:
        print("Ra2ce handler not yet initiated!")
        return

    Ra2ceGUI.ra2ceHandler.configure()

    get_graphs = ['origins_destinations_graph']
    for g in get_graphs:
        Ra2ceGUI.graph = Ra2ceGUI.ra2ceHandler.input_config.network_config.graphs[g]

        # create dictionary of the roads geometries
        edge_list = [e for e in Ra2ceGUI.graph.edges.data(keys=True) if "geometry" in e[-1]]
        inverse_vertices_dict = {}
        for i, line in enumerate(edge_list):
            inverse_vertices_dict.update(
                {p: (line[0], line[1], line[2]) for p in set(list(line[-1]["geometry"].coords))})

        # create list of all points to search in
        all_vertices = np.array([p for p in list(inverse_vertices_dict.keys())])

        def closest_node(node, nodes):
            deltas = nodes - node
            dist_2 = np.einsum('ij,ij->i', deltas, deltas)
            return nodes[np.argmin(dist_2)]

        closest_node_on_road = closest_node(np.array((coords['lng'], coords['lat'])), all_vertices)
        closest_u_v_k = inverse_vertices_dict[(closest_node_on_road[0], closest_node_on_road[1])]
        Ra2ceGUI.graph.edges[closest_u_v_k[0], closest_u_v_k[1], closest_u_v_k[2]]['F_EV1_ma'] = Ra2ceGUI.edited_flood_depth

        # Highlight the selected road in yellow in the interface
        to_highlight = Ra2ceGUI.graph.edges[closest_u_v_k[0], closest_u_v_k[1], closest_u_v_k[2]]["geometry"]
        Ra2ceGUI.highlight_road(to_highlight, 'Road network', 'selected_road')

        # TODO do this always immediately or only after someone is done editing?
        from ra2ce.io.writers.multi_graph_network_exporter import MultiGraphNetworkExporter
        exporter = MultiGraphNetworkExporter(basename=g, export_types=["pickle"])
        exporter.export_to_pickle(Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data["static"].joinpath("output_graph"),
                                  Ra2ceGUI.graph)


def showRoads():
    Ra2ceGUI.show_roads()


def selectFloodmap():
    _loaded_floodmap = openFileNameDialog(Ra2ceGUI.current_project.joinpath('static', 'hazard'),
                                          fileTypes=["GeoTIFF files (*.tif)"])
    if _loaded_floodmap:
        Ra2ceGUI.loaded_floodmap = Path(_loaded_floodmap)
        Ra2ceGUI.update_flood_map()
        Ra2ceGUI.gui.setvar("ra2ceGUI", "loaded_floodmap", Path(Ra2ceGUI.loaded_floodmap).name)

        # Update all GUI elements
        Ra2ceGUI.gui.update()
