import pandas as pd
import networkx as nx
import streamlit as st
from random import choices
import osmnx as ox
import geopandas as gpd

import folium
from folium import plugins
from streamlit_folium import folium_static

from shortest_path import get_short_path_graph
from tools import *

LOGO = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/ArcGIS_logo_%28cropped%29.png/128px-ArcGIS_logo_%28cropped%29.png'
APP_TITLE = 'GIS'
st.set_page_config(layout='wide', page_icon=LOGO, page_title=APP_TITLE)

# Load DATA:
graph = nx.read_gpickle('./data/graph1.gpickle')
nodes = pd.read_csv('./data/nodes.csv')
edges = pd.read_csv('./data/edges.csv')
# nodes = gpd.read_file('./data/nodes.shp')
# edges = gpd.read_file('./data/edges.shp')

evacuation_points = [8104348645, 2862602003, 8510058624, 1774432269, 8531352025]

# Генерация эфакуаионных пунктов
nodes['is_evacuation'] = 0
nodes.loc[nodes['osmid'].isin(evacuation_points), 'is_evacuation'] = 1

# Simulate loading capacity for heatmap
population = [0, 1, 2]
weights = [0.7, 0.2, 0.1]

# Heatmap will be based on middle points
# of edges:

mid_x = ((edges.geometry.str.replace(
    ')', '').str.replace(
        '(', '').str.replace(
            ',', '').str.split(' ').str[1].astype(float)
 + edges.geometry.str.replace(
    ')', '').str.replace(
        '(', '').str.replace(
            ',', '').str.split(' ').str[3].astype(float)
) 
/ 2)

mid_y = ((edges.geometry.str.replace(
    ')', '').str.replace(
        '(', '').str.replace(
            ',', '').str.split(' ').str[2].astype(float)
 + edges.geometry.str.replace(
    ')', '').str.replace(
        '(', '').str.replace(
            ',', '').str.split(' ').str[4].astype(float)
) 
/ 2)

edges['mid_x'] = mid_x
edges['mid_y'] = mid_y

# HeatMap data according to points
_y = edges['mid_y'].tolist()
_x = edges['mid_x'].tolist()
_heat = [choices(population, weights) for i in range(len(_y))]
heatmap_data = [[_y[i], _x[i], _heat[i][0]] for i in range(len(_y))]

# Assign choices list to workload
edges['workload'] = [elem[0] for elem in _heat]
geometry = edges['geometry'].tolist()
workload = edges['workload'].tolist()

# Functions to calculate speed and travel time according to traffic jam:
def calculate_speed(speed, workload):
    if workload==2:
        return 10
    elif workload==1:
        return 25
    else:
        return speed
    
def calculate_travel_time(length, speed):
    '''
    length - in meters
    speed - in kph
    '''
    return round(length/(speed*1000/3600), 1)

# Apply calc_speed function:
edges['speed_kph_1'] = edges.apply(
    lambda row: calculate_speed(
        row['speed_kph'], 
        row['workload']
    ), 
    axis=1
)

# Apply calc_time function:
edges['travel_tim_1'] = edges.apply(
    lambda row: calculate_travel_time(
        row['length'], 
        row['speed_kph_1']
    ), 
    axis=1
)

# Recreate graph from edges df:
G = nx.from_pandas_edgelist(
    df=edges, 
    source="u", 
    target="v", 
    edge_attr=["name", "length", "speed_kph_1", "travel_tim_1", "from", "to", "workload"],
    create_using=nx.MultiGraph())


with st.sidebar:
	st.sidebar.write(f'# GIS')
	
	# user_location = st.sidebar.number_input("Ваше местоположение", value=6547432844, min_value=0)
	user_location = st.sidebar.selectbox(
		"Ваше местоположение", nodes['osmid'].tolist(), index=0
	)
	map_tile = st.sidebar.radio(
		"Выберите тип отображения карты", ["OpenStreetMap", "CartoDBpositron"], index=0
	)
	st.sidebar.info("Вам автоматически предложен ближайший эвокуационный пункт, с учетом оптимальных путей, но вы можете изменить его.")
	ev_point = st.sidebar.selectbox(
		"Эвокуационный пункт", [None, 8104348645, 2862602003, 8510058624, 1774432269, 8531352025], index=0
	)

	# heatmap_type = st.sidebar.checkbox("Показать карту загруженности")
	heatmap_type = st.sidebar.radio(
		"Выберите тип карты по загруженности", ["Убрать", "HeatMap", "Дороги"], index=0
	)


# calc short path
path_coords = get_short_path_graph(G=G, nodes=nodes, node_a=user_location, node_b=ev_point)


# MAP with folium
m = folium.Map(width='100%', height='100%', location=[51.154811, 71.419517], zoom_start=12, min_zoom=10, max_bounds=False, tiles=map_tile)

# Customize of map
# Heatmap
from tqdm import tqdm
if heatmap_type == 'HeatMap':
	get_heatmap(heatmap_data).add_to(m)
elif heatmap_type == 'Дороги':
	for i in tqdm(range(len(geometry))):
		x1, y1 = geometry[0][12:-1].split(', ')[0].split(' ')
		x2, y2 = geometry[0][12:-1].split(', ')[1].split(' ')

		path = [[y1, x1], [y2, x2]]
		color = None
		if workload[i]==0:
			color = 'green'
		elif workload[i]==1:
			color = 'yellow'
		elif workload[i]==2:
			color = 'red'

		get_road(path, color).add_to(m)


# Markers
get_home(path_coords[0]).add_to(m)
circle_marker(path_coords[-1], 'Эвокуационный пункт 1').add_to(m)

# Path
get_antpath(path_coords).add_to(m)

# Layers
get_layer_control().add_to(m)


folium_static(m, width=1450, height=830)