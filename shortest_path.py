import warnings
warnings.filterwarnings("ignore")

import pandas as pd
pd.set_option('display.max_columns', None)
import geopandas as gpd
import networkx as nx
import osmnx as ox
ox.config(use_cache=True, log_console=False)
import random
import re

def get_short_path_graph(G, nodes, node_a, node_b, ):
    # Input: User location(Start point):
    #        datatype - POINT ShapeFile,
    #        Destination:
    #        datatype - POINT ShapeFile
    # Output: Path:
    #         datatype - List of osmids
    
    node_b = (4959701273 if node_b==None else node_b)

    # Getting shortest path
    route = nx.shortest_path(G, source=node_a, target=node_b, weight="travel_tim_1")
    
    coordinates = []
    for x in route:
        coordinates.append([nodes[nodes['osmid']==x]['y'].to_list()[0], nodes[nodes['osmid']==x]['x'].to_list()[0]])

    return coordinates