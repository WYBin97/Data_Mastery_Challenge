import random
import geopandas as gpd
from shapely.geometry import LineString, Point

def generate_random_points_along_line(lines_gdf, number_of_points=1, buffer_distance=0):
    random_points = []

    for _, row in lines_gdf.iterrows():
        line = row['geometry']
        
        if buffer_distance > 0:
            line = line.buffer(buffer_distance)

        line_length = line.length
        for _ in range(number_of_points):
            random_distance = random.uniform(0, line_length)
            random_point = line.interpolate(random_distance)
            
            if buffer_distance > 0:
                if line.contains(random_point):
                    random_points.append(random_point)
            else:
                random_points.append(random_point)

    return gpd.GeoDataFrame({'geometry': random_points})