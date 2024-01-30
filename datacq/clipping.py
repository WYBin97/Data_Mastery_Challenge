import geopandas as gpd
from shapely.geometry import shape

# Load the Kampala boundary GeoJSON file
kampala_gdf = gpd.read_file('great_kampala.geojson')

# Ensure that the geometry type of Kampala boundary is a MultiPolygon
kampala_boundary = shape(kampala_gdf['geometry'][0])

# Check and repair the Kampala boundary if it's invalid
if not kampala_boundary.is_valid:
    kampala_boundary = kampala_boundary.buffer(0)

# Load the category GeoJSON file (e.g., 'built_up.geojson', 'water.geojson', etc.)
category_gdf = gpd.read_file('polygon_water.geojson')  # Replace 'category_file.geojson' with your file name

# Check and repair invalid geometries in the category file
category_gdf['geometry'] = category_gdf.geometry.buffer(0).where(~category_gdf.is_valid, category_gdf.geometry)

# Optionally simplify geometries if they are too complex (tweak tolerance as needed)
tolerance = 0.00001
kampala_boundary = kampala_boundary.simplify(tolerance, preserve_topology=True)
category_gdf['geometry'] = category_gdf.geometry.simplify(tolerance, preserve_topology=True)

# Clip the category geometries with the Kampala boundary
clipped_gdf = gpd.clip(category_gdf, kampala_boundary)

# Remove empty geometries if any
clipped_gdf = clipped_gdf[~clipped_gdf.is_empty]

# Save the clipped geometries to a new GeoJSON file if not empty
if not clipped_gdf.empty:
    clipped_gdf.to_file('clipped_water.geojson', driver='GeoJSON')  # Replace 'clipped_water.geojson' with your desired output file name
    print("GeoJSON file has been clipped and saved.")
else:
    print("No geometries within the clipping boundary.")
