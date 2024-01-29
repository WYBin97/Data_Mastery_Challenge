import geopandas as gpd
import pandas as pd

def merge_points(*args):
    merged_gdf = gpd.GeoDataFrame(pd.concat(args, ignore_index=True))
    return merged_gdf