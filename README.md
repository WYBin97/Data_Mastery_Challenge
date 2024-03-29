# USER WORKFLOW MANUAL
![openspacemapping](https://github.com/WYBin97/Data_Mastery_Challenge/assets/50994180/4834e41f-35ce-4b54-9f63-c8c8256e58e9)


## General Guidelines
- **General #1**: Upon opening a new `.py` file, make sure you import or have downloaded the necessary modules stated at the top of the file. This can be done by opening a terminal and running: `pip install MODULENAME`
- **General #2**: Not all input must be changed; some are optional and can be changed based on user desire. Use logical thinking.
- **General #3**: Read carefully and understand the hashed comments providing explanations.

## Requirements
- Python 3.8 or higher
- Google Earth Engine account
- Area of Interest (AoI) in geo-spatial format (preferably geojson) and its bounding box. You will need the bounding box to get the data, and the area of interest to filter it.
- An IDE like VSCode will help you to adjust the code, especially the variables, output name, and input name.

## Dependencies
- requests: [Documentation](https://requests.readthedocs.io/en/latest/)
- shapely: [Documentation](https://shapely.readthedocs.io/en/stable/manual.html)
- pandas: [Documentation](https://pandas.pydata.org/getting_started.html)
- geopandas: [Documentation](https://geopandas.org/en/stable/getting_started.html)

## Installation
- You can get/clone the repository through SSH Authentication, https, or downloading as a zip. The necessary files are in the folder `src`. For beginners, we recommend using zip download. In this GitHub repository, browse to and download the folder `src`, unzip it, and save it on your machine.

## Phase 1: Data Acquisition
### Goal: Getting OSM data of 4 categories
1. Open the file `/src/phase-01_get_osm.py` using your IDE or your local text editor.
2. Define the bounding box by entering coordinates of your study area.
   - Format of the bounding box: “min_latitude, min_longitude, max_latitude, max_longitude”. Ex: `"0.0097394039291600, 32.4057359175773030, 0.5085509362294360, 32.7963300045455028"`
3. In open space mapping, we need four categories: Built-up, Grayspace (Open space without vegetation), Greenspace (Open space with vegetation), and Water Bodies. In this file, we have defined what the key-value pairs for each category are. In lines 7-26, you can activate a class query by removing the `//` (double slash) and turn off a class query by adding it.
4. In line 37, you can change the output name by changing `with open('osm_data_builtup.xml', 'wb')` to your need.
5. Run the code four times, each run for each category. Note that you have to change the name of the outputs accordingly.

## Phase 2: Data Pre-Processing
### Part 2.1: Translating Highway to Polygon
#### Goal: Transform the highway line data of grayspace to polygon in geojson format
1. Open the file `/src/phase_02-1_line_buffer.py` using your IDE or your local text editor.
2. In line 7, optionally you can change the buffer distance according to your satellite imagery choice in `BUFFER_DISTANCE = 0.000063`. We chose to use Sentinel-2 which has 10 m and 20 m resolution. Therefore, we use 7 m for this. However, you need to convert meters to degrees. 1 meter is approximately 0.000018 degrees.
3. In line 10, change the file in this code to your grayspace xml file `tree = ET.parse('osm_data_grayspace.xml')`
4. In line 41, you can also set the output name by changing the output name in `with open('grayspace_polygon.geojson', 'w') as f:`
5. Run the code once.

### Part 2.2: Converting XML to GeoJSON
#### Goal: Convert the XML file from 2.1 to be in GeoJSON Format
1. Open the file `/src/phase_2-2_xmltogeojson.py`.
2. In line 69, provide a directory with your `.xml` file in `osm_xml_file = 'osm_data_builtup.xml'`
3. In line 70, provide a directory with your empty `.geojson` file in `output_geojson_file = 'polygon_builtup.geojson'`
4. Run the file three times for Built-up, Greenspace, and Water Bodies.

### Part 2.3: Clipping
#### Goal: Clip the output data to your AoI
1. Open the file `/src/phase_02-3_clipping.py`.
2. In line 5, provide the name of your `.geojson` boundary file (note: this file must be in the same folder as the script location) in `kampala_gdf = gpd.read_file('great_kampala.geojson')`. Make sure to also change this name in line 8.
3. In line 15, provide the name of your OSM category file that you created using the get_osm file in `category_gdf = gpd.read_file('polygon_water.geojson')`.
4. In line 33, provide the output name of the clipped file in `clipped_gdf.to_file('clipped_water.geojson', driver='GeoJSON')`.
5. Run the file four times, each run for each category. Note that you have to change the name of the outputs accordingly.

### Part 2.4: Creating Random Points
#### Goal: Creating random points within a polygon with a minimum distance
1. Open the file `/src/phase_02_4_random_points.py`.
2. In line 31, provide the name of your clipped category `.geojson` file in `category_geojson_file = 'clipped_water.geojson'`.
3. In line 32, provide the name of your output outfile in `output_points_geojson_file = 'points_water.geojson'`.
4. In line 33, optionally you can change the minimum distance between points according to your satellite imagery pixel size in `min_distance = 0.00045`.
5. In line 34, optionally you can change the number of points made in `num_points = 1000`.
6. Run the file four times, each run for each category. Note that you have to change the name of the outputs accordingly.

### Part 2.5: Merge
#### Goal: Merging points made into one shapefile file
1. Open the file `/src/phase_02_5_merge.py`.
2. In line 5, enter all your created category `.geojson` files with their corresponding class values.
3. In line 23, you can change the output file name in `output_file = 'sample2'`.
4. Run the file once.

*User Workflow for SENTINEL-2 PROCESSING and OPEN SPACE MAPPING are documented within the script for readability and sharing. The result file from the merge is a shapefile, and you will need to upload it to GEE Asset.*

## Phase 3: Sentinel-2 Image Processing
- **Code**: [Google Earth Engine Script](https://code.earthengine.google.com/e8fb7091bff277f9ee49970b3bfece25)
- **Goal**: Processing Sentinel-2 imagery with recommended bands and indices for processing urban open space classification as mentioned in Aguilar and Kuffer (2020).
- **User Input Customization in the `S2_Processing` function**:
  - **Change Time Interval**: Replace `Date_Start` and `Date_End` with your desired date in the format: `YYYY-MM-DD` to get the desired time period.
  - **Change Cloud Percentage**: Replace `Cloud_Percentage` with a numerical value (recommended: 0-20, a lower value will generate a clearer image).
  - **Change Area_Of_Interest** (2 options available):
    - **Option 1**: Define shapefile using the CRS: WGS84 ESPG 4326 and replace `Area_Of_Interest` with the uploaded shapefile in GEE Assets.
    - **Option 2**: Draw a polygon within the Google Earth Engine Map, the polygon variable name (`geometry`) will appear and replace this with `Area_Of_Interest`.
- **Exporting**: Area of interest and Sentinel-2 imagery are exported in GEE Assets; navigate to the Tasks panel on the left and select Run.
- **Example Code**: `print('Sentinel-2 Cloud-Free Image Composite & Indices', S2_Processing('2023-01-01', '2023-12-30', 5, 'projects/data-mastery-challenge-sharing/assets/great_kampala'));`
- **Execution**: Run the code.

## Phase 4: Random Forest Classification
- **Code**: [Google Earth Engine Script](https://code.earthengine.google.com/1ca471c1c121841cff2378fc5036a8a6)
- **Goal**: Classifying the Sentinel-2 imagery through a Random Forest model using samples from OSM data.
- **User Input Customization in the `RF_Classification` function**:
  - **Change Area_Of_Interest**: As exported from the previous phase, i.e., Sentinel-2 Processing, `Area_Of_Interest` is imported from GEE Assets.
  - **Change Sentinel2_Cloud_Free_Image**: As exported from the previous phase, `Sentinel2_Cloud_Free_Image` is imported from GEE Assets.
  - **Change Land_Cover_Classifier_Vector_Points**: Data from the previous Sample Acquisition step is uploaded as GEE Assets and input as `Land_Cover_Classifier_Vector_Points`.
- **Exporting**: Sentinel 2 Classified Map and Confusion Matrix are exported to Drive for sharing; navigate to the Tasks panel on the left and select Run.
- **Example Code**: `print(RF_Classification('projects/data-mastery-challenge-sharing/assets/Area_of_Interest', 'projects/data-mastery-challenge-sharing/assets/Sentinel_2_Cloud_Free_Image_Composite', 'projects/data-mastery-challenge-sharing/assets/land_cover_reference_data_2023'));`
- **Execution**: Run the code.

*You can then process the exported image into vector and stylize it in your local geospatial software. This is the result of our urban space mapping in Kampala:*

![Urban_Open_Space_Map](https://github.com/WYBin97/Data_Mastery_Challenge/assets/50994180/b41646b4-0364-4f8d-a3f4-252aa5de547a)

