import geopandas as gpd
import pandas as pd

# File paths
geojson_files = {
    'points_builtup.geojson': 0,  # Class code 0
    'points_grayspace.geojson': 1, # Class code 1
    'points_greenspace.geojson': 2, # Class code 2
    'points_water.geojson': 3 # Class code 3
}

# Load each GeoJSON into a GeoDataFrame and assign class code
gdfs = []
for file_path, class_code in geojson_files.items():
    gdf = gpd.read_file(file_path)
    gdf['class'] = class_code
    gdfs.append(gdf)

# Concatenate all GeoDataFrames into one
merged_gdf = pd.concat(gdfs, ignore_index=True)

# Save the merged GeoDataFrame to a new Shapefile
output_file = 'sample2'  # No need for file extension, it will be added automatically
merged_gdf.to_file(output_file, driver='ESRI Shapefile')
print(f"Merged Shapefile has been saved to {output_file}.shp.")