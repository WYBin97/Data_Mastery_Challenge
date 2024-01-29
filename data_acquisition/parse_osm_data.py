import xml.etree.ElementTree as ET
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd

def parse_osm_data(xml_data):
    root = ET.fromstring(xml_data)
    
    built_up_polygons = []
    greenspace_polygons = []
    grayspace_lines = []
    water_bodies_polygons = []

    for element in root.findall('way'):
        nd_refs = []
        for nd in element.findall('nd'):
            nd_refs.append(nd.get('ref'))
        
        coords = []

        for nd_ref in nd_refs:
            node = root.find(f".//node[@id='{nd_ref}']")
            if node is not None:
                lat = float(node.get('lat'))
                lon = float(node.get('lon'))
                coords.append((lon, lat)) 

        tags = {tag.get('k'): tag.get('v') for tag in element.findall('tag')}
        if 'building' in tags:
            built_up_polygons.append(Polygon(coords))
        elif tags.get('natural') == 'water' or tags.get('landuse') == 'basin':
            water_bodies_polygons.append(Polygon(coords))
        elif 'natural' in tags:
            greenspace_polygons.append(Polygon(coords))
        elif 'highway' in tags and tags['highway'] in ['motorway', 'primary', 'secondary', 'tertiary']:
            grayspace_lines.append(LineString(coords))

    built_up_gdf = gpd.GeoDataFrame({'geometry': built_up_polygons})
    greenspace_gdf = gpd.GeoDataFrame({'geometry': greenspace_polygons})
    grayspace_gdf = gpd.GeoDataFrame({'geometry': grayspace_lines})
    water_bodies_gdf = gpd.GeoDataFrame({'geometry': water_bodies_polygons})

    return built_up_gdf, greenspace_gdf, grayspace_gdf, water_bodies_gdf