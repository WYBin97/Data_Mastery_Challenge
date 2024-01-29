import requests
import os

def query_overpass_api_and_save_xml(bbox):
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
    [out:xml];
    (
      // Built-Up
      way["building"](bbox);
      relation["building"](bbox);
      // Greenspace
      way["natural"](bbox);
      relation["natural"](bbox);
      // Grayspace (only highways for now, will convert to polygons later)
      way["highway"~"motorway|primary|secondary|tertiary"](bbox);
      // Water Bodies
      way["natural"="water"](bbox);
      relation["natural"="water"](bbox);
      way["landuse"="basin"](bbox);
      relation["landuse"="basin"](bbox);
    );
    out body;
    >;
    out skel qt;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})
    if response.status_code == 200:
        return response.text
    else:
        return None

bbox = "0.0097394039291600,32.4057359175773030,0.5085509362294360,32.7963300045455028"

xml_data = query_overpass_api_and_save_xml(bbox)

if xml_data:
    file_path = os.path.join(os.getcwd(), "osm_kampala_amenities.xml")
    with open(file_path, "w") as file:
        file.write(xml_data)
    print(f"Data saved to {file_path}")
else:
    print("Failed to retrieve data from the Overpass API.")
