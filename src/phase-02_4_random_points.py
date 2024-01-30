import geopandas as gpd
import random
from shapely.geometry import Point, mapping
from shapely.ops import unary_union
import geojson

def generate_points_within_polygon(polygon, num_points, min_distance):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    attempts = 0
    max_attempts = num_points * 100  # to prevent an infinite loop
    
    while len(points) < num_points and attempts < max_attempts:
        attempts += 1
        point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if polygon.contains(point):
            if all(point.distance(existing_point) >= min_distance for existing_point in points):
                points.append(point)
    
    return points

def save_geojson(points, output_file):
    features = [geojson.Feature(geometry=mapping(point), properties={}) for point in points]
    feature_collection = geojson.FeatureCollection(features)

    with open(output_file, 'w') as f:
        geojson.dump(feature_collection, f)
    print(f"GeoJSON file has been saved to {output_file}.")

# Usage
category_geojson_file = 'clipped_water.geojson'  # Replace with your actual polygon file
output_points_geojson_file = 'points_water.geojson'  # Replace with your desired output file
min_distance = 0.00045  # Minimum distance in degrees (approx 50 meters)
num_points = 1000

# Load the polygon
category_gdf = gpd.read_file(category_geojson_file)
polygon = unary_union(category_gdf.geometry)  # Combine all geometries into a single one if there are multiple

# Generate points
generated_points = generate_points_within_polygon(polygon, num_points, min_distance)

# Save points to GeoJSON
save_geojson(generated_points, output_points_geojson_file)
