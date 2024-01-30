import xml.etree.ElementTree as ET
from shapely.geometry import LineString, mapping
from shapely.ops import unary_union
import geojson

# Constants
BUFFER_DISTANCE = 0.000063  # approximately 7 meters in degrees

# Parse the XML file
tree = ET.parse('osm_data_grayspace.xml')
root = tree.getroot()

# Extract nodes (for node references in ways)
nodes = {}
for node in root.findall('node'):
    id = node.get('id')
    lat = float(node.get('lat'))
    lon = float(node.get('lon'))
    nodes[id] = (lon, lat)  # Note: GeoJSON uses (lon, lat)

# Process grayspace (highways)
grayspace_geometries = []
for element in root.findall('way'):
    tags = {tag.get('k'): tag.get('v') for tag in element.findall('tag')}
    if 'highway' in tags and tags['highway'] in ['motorway', 'primary', 'secondary', 'tertiary']:
        # Create the geometry
        nd_refs = [nd.get('ref') for nd in element.findall('nd')]
        points = [nodes[ref] for ref in nd_refs if ref in nodes]
        if points:
            line = LineString(points)
            buffered_line = line.buffer(BUFFER_DISTANCE)
            grayspace_geometries.append(buffered_line)

# Combine geometries into a MultiPolygon
combined_grayspace = unary_union(grayspace_geometries)

# Convert to GeoJSON
geojson_geom = geojson.Feature(geometry=mapping(combined_grayspace), properties={"category": "grayspace"})

# Save to file
with open('grayspace_polygon.geojson', 'w') as f:
    geojson.dump(geojson_geom, f)

print("GeoJSON file for grayspace has been saved.")
