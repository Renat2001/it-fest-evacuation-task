import folium
from folium import Map, TileLayer, LayerControl, PolyLine, Marker, CircleMarker
from folium.plugins import HeatMap, AntPath
from folium.utilities import normalize

from jinja2 import Template

def get_heatmap(heatmap_data):
	return HeatMap(heatmap_data, name='HeatMap')

def get_tile_cartoDB():
	return TileLayer('CartoDBpositron')

def get_path(path_coords):
	return PolyLine(locations=path_coords, weight=5, color='red')

def get_road(path_coords, color):
	return PolyLine(locations=path_coords, weight=5, color=color)

def get_layer_control():
	return LayerControl()

def get_home(coord):
	return Marker(
		coord,
		popup="<strong>Ваше местоположение</strong>",
		tooltip="Кликните для дополнительной информаций",
		icon=folium.Icon(
			color='green',
			icon='home',
			prefix='fa'
		)
	)


def get_antpath(path_coords):
	return AntPath(locations=path_coords)

	out = m._parent.render()

	# We verify that the script import is present.
	script = '<script src="https://cdn.jsdelivr.net/npm/leaflet-ant-path@1.1.2/dist/leaflet-ant-path.min.js"></script>'  # noqa
	assert script in out

	# We verify that the script part is correct.
	tmpl = Template("""
		  {{this.get_name()}} = L.polyline.antPath(
				  {{ this.locations|tojson }},
				  {{ this.options|tojson }}
				)
				.addTo({{this._parent.get_name()}});
		""") 

	expected_rendered = tmpl.render(this=antpath)
	rendered = antpath._template.module.script(antpath)
	assert normalize(expected_rendered) == normalize(rendered)

	return antpath


def circle_marker(coord, popup):
	return CircleMarker(
		location=coord,
		radius=20,
		popup=popup,
		tooltip="Кликните для дополнительной информаций",
		color='#428bca',
		fill=True,
		fill_color='#428bca'
	)