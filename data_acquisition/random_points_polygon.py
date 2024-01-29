from shapely.geometry import Point
import random
import geopandas as gpd

def generate_random_points_in_polygon(polygons_gdf, number_of_points=1):
    random_points = []

    for _, row in polygons_gdf.iterrows():
        polygon = row['geometry']
        minx, miny, maxx, maxy = polygon.bounds
        points_generated = 0
        
        while points_generated < number_of_points:
            pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if polygon.contains(pnt):
                random_points.append(pnt)
                points_generated += 1

    return gpd.GeoDataFrame({'geometry': random_points})