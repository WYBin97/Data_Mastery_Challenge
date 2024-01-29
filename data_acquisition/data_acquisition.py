from get_osm import query_overpass_api_and_save_xml
from parse_osm_data import parse_osm_data
from random_points_polygon import generate_random_points_in_polygon
from random_points_line import generate_random_points_along_line
from merge_points import merge_points
import os

def main_workflow(bbox, number_of_points, buffer_distance_for_grayspace):
    xml_data = query_overpass_api_and_save_xml(bbox)
    if not xml_data:
        print("Failed to retrieve data from the Overpass API.")
        return

    built_up_gdf, greenspace_gdf, grayspace_gdf, water_bodies_gdf = parse_osm_data(xml_data)

    random_built_up_points = generate_random_points_in_polygon(built_up_gdf, number_of_points)
    random_greenspace_points = generate_random_points_in_polygon(greenspace_gdf, number_of_points)
    random_water_bodies_points = generate_random_points_in_polygon(water_bodies_gdf, number_of_points)

    random_grayspace_points = generate_random_points_along_line(grayspace_gdf, number_of_points, buffer_distance_for_grayspace)

    all_random_points = merge_points(random_built_up_points, random_greenspace_points, random_grayspace_points, random_water_bodies_points)

    output_file_path = os.path.join(os.getcwd(), "merged_random_points.geojson")
    all_random_points.to_file(output_file_path, driver='GeoJSON')
    print(f"Merged data saved to {output_file_path}")

if __name__ == "__main__":
    bbox = "0.0097394039291600,32.4057359175773030,0.5085509362294360,32.7963300045455028"
    number_of_points_per_polygon = 1000
    buffer_distance_for_grayspace = 0.00045
    main_workflow(bbox, number_of_points_per_polygon, buffer_distance_for_grayspace)
