import xml.etree.ElementTree as ET
from shapely.geometry import Polygon, MultiPolygon, mapping
import geojson

def parse_osm_xml(osm_xml_file):
    tree = ET.parse(osm_xml_file)
    root = tree.getroot()

    nodes = {}
    ways = {}
    multipolygons = []

    # Parse nodes
    for node in root.findall('node'):
        id = node.get('id')
        lat = float(node.get('lat'))
        lon = float(node.get('lon'))
        nodes[id] = (lon, lat)  # GeoJSON uses (lon, lat)

    # Parse ways
    for way in root.findall('way'):
        id = way.get('id')
        nd_refs = [nd.get('ref') for nd in way.findall('nd')]
        ways[id] = [nodes[ref] for ref in nd_refs if ref in nodes]

    # Find multipolygons (relations of type 'multipolygon')
    for relation in root.findall('relation'):
        tags = {tag.get('k'): tag.get('v') for tag in relation.findall('tag')}
        if tags.get('type') == 'multipolygon':
            outer_ways_coords = []
            inner_ways_coords = []
            for member in relation.findall('member'):
                if member.get('type') == 'way' and member.get('ref') in ways:
                    way_coords = ways[member.get('ref')]
                    if len(way_coords) >= 4:  # Ensure there are at least 4 coordinates
                        if member.get('role') == 'outer':
                            outer_ways_coords.append(way_coords)
                        elif member.get('role') == 'inner':
                            inner_ways_coords.append(way_coords)
            
            # Create the multipolygon structure
            for outer_way_coords in outer_ways_coords:
                # Find inner ways (holes) within this outer way
                holes = [inner_way for inner_way in inner_ways_coords if is_inner_within_outer(inner_way, outer_way_coords)]
                # Create a polygon with holes, but ensure there are enough coordinates
                if len(outer_way_coords) >= 4:
                    polygon = Polygon(shell=outer_way_coords, holes=holes)
                    multipolygons.append(polygon)

    return multipolygons

def is_inner_within_outer(inner_way, outer_way):
    inner_poly = Polygon(inner_way)
    outer_poly = Polygon(outer_way)
    return inner_poly.within(outer_poly)

def save_geojson(multipolygons, output_file):
    # Convert Multipolygons to GeoJSON
    features = [geojson.Feature(geometry=mapping(mp), properties={}) for mp in multipolygons]
    feature_collection = geojson.FeatureCollection(features)

    # Save to file
    with open(output_file, 'w') as f:
        geojson.dump(feature_collection, f)

    print(f"GeoJSON file has been saved to {output_file}.")

# Usage
osm_xml_file = 'osm_data_builtup.xml'  # Replace with your OSM XML file
output_geojson_file = 'polygon_builtup.geojson'  # Replace with your desired output GeoJSON file
multipolygons = parse_osm_xml(osm_xml_file)
save_geojson(multipolygons, output_geojson_file)
