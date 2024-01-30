var S2_Processing = function (Date_Start, Date_End, Cloud_Percentage, Area_Of_Interest){
  
  // Declare Relevant Variables & Parameters
  var start_date = Date_Start;
  var end_date = Date_End;
  var cloud_perc = Cloud_Percentage;
  var AOI = ee.FeatureCollection(Area_Of_Interest);
  var SAVI_factor = 0.5;  /* SAVI (Soil Adjusted Vegetation Index) includes brightness correction factor; range from (0-1) */
  var S2imageVisParam = {"opacity":1,"bands":["B4","B3","B2"],min: 0.01, max: 0.13, "gamma":1}; /* Sentinel-2 Visualisation Parameter */

  // Process Sentinel-2 Imagery
  var S2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                  .filterBounds(AOI) 
                  .filterDate(start_date, end_date)
                  .filterMetadata("CLOUDY_PIXEL_PERCENTAGE",'less_than', cloud_perc)
                  .map(maskS2clouds_SCL);

      function maskS2clouds_SCL(image) {  /* Cloud Mask Operator */
        var qa = image.select('SCL');
        var shadowBitMask = 1 << 3;
        var cloud1BitMask = 1 << 8;
        var cloud2BitMask = 1 << 9;
        var cirrusBitMask = 1 << 10;
        var mask = qa.bitwiseAnd(shadowBitMask).eq(0)
            .and(qa.bitwiseAnd(cloud1BitMask).eq(0))
            .and(qa.bitwiseAnd(cloud2BitMask).eq(0))
            .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
        return image.updateMask(mask).divide(10000);
      }
    
    // -----------------------------Median Value Of Image Collection
    var S2median = S2.median().clip(AOI); 
    
    // -----------------------------Bands For Spectral Indices
    var R = S2median.select('B4');
    var G = S2median.select('B3');
    var B = S2median.select('B2');
    var RE1 = S2median.select('B5');
    var RE2 = S2median.select('B6');
    var RE3 = S2median.select('B7');
    var NIR = S2median.select('B8');
    var RE4 = S2median.select('B8A');
    var SWIR1 = S2median.select('B11');
    var SWIR2 = S2median.select('B12');
    
    var L = SAVI_factor; /* Rename SAVI brightness correction factor for readability */
    
      // -----------------------------Enhance Vegation Index (EVI)
      var evi = S2median.expression(
        '2.5* (NIR - R) /((NIR + 6.0*R - 7.5*B) + 1.0)',{
          'NIR' : NIR,
          'R' : R,
          'B' : B,
        }).rename('evi');
    
      // -----------------------------Transformed Chlorophyll Absorption in Reflectance Index (TCARI)
      var tcari = S2median.expression(
        '3*((RE - R) - 0.2* (RE - R) * (RE/R))',{
          'RE' : RE1,
          'R' : R,
        }).rename('tcari');
    
      // -----------------------------Soil Adjusted Vegetation Index (SAVI)
      var savi = S2median.expression(
        '(1 + L)*(NIR - R)/(NIR + R + L)',{
          'NIR' : NIR,
          'R' : R,
          'L' : L,
        }).rename('savi');
        
      // -----------------------------Modified Soil Adjusted Vegetation Index (MSAVI)
      var msavi = S2median.expression(
        '0.5*(2*NIR + 1 - sqrt((2*NIR + 1)*(2*NIR + 1) - 8*(NIR - R)))',{
          'NIR' : NIR,
          'R' : R,
        }).rename('msavi');
        
      // -----------------------------Visible Atmospherically Resistance Index 700 (VARI700)
      var vari = S2median.expression(
        '(RE - 1.7*R + 0.7*B)/(RE + 2.3*R - 1.3*B)',{
          'R' : R,
          'B' : B,
          'RE' : RE1,
        }).rename('vari');
      
      // -----------------------------Green Leaf Index (GLI)
      var gli = S2median.expression(
        '(2*G - R - B)/(2*G + R + B)',{
          'G' : G,
          'R' : R,
          'B' : B,
        }).rename('gli');
    
      // -----------------------------Normalized Difference Vegetation Index (NDVI)
      var ndvi = S2median.expression(
        '(NIR - R)/(NIR + R)',{
          'NIR' : NIR,
          'R' : R,
        }).rename('ndvi');
    
      // -----------------------------Normalized Difference Water Index (NDWI)
      var ndwi = S2median.expression(
        '(G - NIR)/(G + NIR)',{
          'NIR' : NIR,
          'G' : G,
        }).rename('ndwi');
    
      // -----------------------------Normalized Difference Built-Up Index (NDBI)
      var ndbi = S2median.expression(
        '(SWIR - NIR)/(SWIR + NIR)',{
          'SWIR' : SWIR1,
          'NIR' : NIR,
        }).rename('ndbi');

  // Composite Sentinel-2 Image With Spectral Indices
  var S2composite = ee.Image([R, G, B, RE1, RE2, RE3, NIR, RE4, SWIR1, SWIR2, evi, tcari, savi, msavi, vari, gli, ndvi, ndwi, ndbi]).float();

  
  // Add Layers to Map
  
  Map.centerObject(AOI, 10);  /* Center Map To AOI */
  
  Map.addLayer(S2composite,S2imageVisParam,'Sentinel-2 Cloud-Free Image, with Indices'); /* Sentinel-2 Cloud-Free Image Composite, with Indices */
  
    // Visualise Area Of Interest (AOI)
    var empty = ee.Image().byte();    /* Create an empty image to paint features, cast to byte */
    var outline_AOI = empty.paint({   /* Paint the polygons boundary */
      featureCollection: AOI,
      color: 1,
      width: 3
    });
    
    Map.addLayer(outline_AOI, {palette: 'FF0000'}, 'AOI', false);

  
  // Download Data To Asset

    // -----------------------------Export Sentinel-2 Cloud-Free Image Composite
    Export.image.toAsset({
      image: S2composite,
      description: 'Sentinel_2_Cloud_Free_Image_Composite',
      scale: 10,
      region: AOI,
      crs: 'EPSG:4326',
      maxPixels: 1e10
    });

    // -----------------------------Export Area Of Interest
    Export.table.toAsset({
      collection: AOI,
      description: 'Area_of_Interest'
    });  
  return(S2composite);
};
/* 
USER INPUT:

User input can be changed in the S2_Processing function below: 
  Change time interval: replace Date_Start and Date_End with desire date in format: YYYY-MM-DD to get desired time period
  Change cloud percentage: replace Cloud_Percentage with numerical value  (recommended: 0-20 , lower value will generate clearer image) 
  Change Area_Of_Interest: (2 options available)
    Option 1. Define shapefile using the CRS: WGS84 ESPG 4326 and replace Area_Of_Interest with the uploaded shapefile in GEE Assets 
    Option 2. Draw a polygon within the Google Earth Engine Map, the polygon variable name (geometry) will appear and replace this with Area_Of_Interest
Area of interest and Sentinel-2 imagery are exported in GEE Assets; Navigate to Tasks panel on left and select Run

Run the code
*/ 
print('Sentinel-2 Cloud-Free Image Composite & Indices', S2_Processing('Date_Start', 'Date_End', Cloud_Percentage, Area_Of_Interest));