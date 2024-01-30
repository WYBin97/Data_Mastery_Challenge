var RF_Classification = function (Area_Of_Interest, Sentinel2_Cloud_Free_Image, Land_Cover_Classifier_Vector_Points){
  
  // Declare Relevant Variables & Parameters
  var img = ee.Image(Sentinel2_Cloud_Free_Image);
  var AOI = ee.FeatureCollection(Area_Of_Interest);
  var lc = ee.FeatureCollection(Land_Cover_Classifier_Vector_Points); /* Input Point Features as label source in classifier training. */

  var classVis = {min: 0, max: 3, palette: ['A9844F' , 'ffff4c', '006400', '33C0FF']};
  var S2imageVisParam = {"opacity":1,"bands":["B4","B3","B2"],min: 0.01, max: 0.13, "gamma":1}; /* Sentinel-2 Visualisation Parameter */

  // Split Vector Points Into 70% (Training Set) and 30% (Validation Set)
  var sample = lc.randomColumn();
  var trainingSample = sample.filter('random <= 0.7');
  var validationSample = sample.filter('random > 0.7');
  
  // Select Bands Of Sentinel-2 Cloud-Free Image Composite
  var bands = ['B4', 'B3', 'B2', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12', 'evi', 'tcari', 'savi', 'msavi', 'vari', 'gli', 'ndvi', 'ndwi', 'ndbi'];

  // Apply Sentinel-2 Bands as the source for Classifier Training and Validation
  var trSet = img.select(bands).sampleRegions({
    collection: trainingSample,
    properties: ['class'], 
    scale: 10,
    geometries: true
  });
  
  var tsSet = img.select(bands).sampleRegions({
    collection: validationSample,
    properties: ['class'], 
    scale: 10,
    geometries: true
  });
  
  // Train a 10-tree Random Forest Classifier from the Training Sample
  var trainedClassifier = ee.Classifier.smileRandomForest(10).train({
    features: trSet,
    classProperty: 'class'
  });
  
  // Get Information about the Trained Classifier
  print('Results of trained classifier', trainedClassifier.explain());
  
  // Get a Confusion Matrix and Overall Accuracy for the Training Sample
  var trainAccuracy = trainedClassifier.confusionMatrix();
  print('Training error matrix', trainAccuracy);
  print('Training overall accuracy', trainAccuracy.accuracy());
  
  // Get a Confusion Matrix and Overall Accuracy for the Validation Sample
  validationSample = tsSet.classify(trainedClassifier);
  var validationAccuracy = validationSample.errorMatrix('class', 'classification');
  print('Validation error matrix', validationAccuracy);
  print('Validation accuracy', validationAccuracy.accuracy());
  
  // Classify the Sentinel-2 Cloud-Free Image from the Trained Classifier
  var imgClassified = img.classify(trainedClassifier);
  
  // Define a nodata value and mask for the masked pixels
  var noDataVal = -999;
  var imgClassifiedunmasked = imgClassified.unmask(noDataVal);
  
  // Add Layers to Map
  
  Map.centerObject(AOI, 10);  /* Center Map To AOI */
  
  Map.addLayer(img,S2imageVisParam,'S2 2023 composite');                        /* Sentinel-2 Cloud-Free Image Composite, with Indices */
  Map.addLayer(lc, classVis, 'lc', false);                                      /* Land Cover Classifier Vector Points */
  Map.addLayer(imgClassified, classVis, 'Classified');                          /* Classified Land Cover Map */
  Map.addLayer(trainingSample, {color: 'black'}, 'Training sample', false);     /* Training Sample Set */
  Map.addLayer(validationSample, {color: 'green'}, 'Validation sample', false); /* Validation Sample Set */
  
  // Download Data To Drive

    // -----------------------------Export Classified Land Cover Map
    Export.image.toDrive({
      image: imgClassifiedunmasked,
      description: 'Sentinel_2_Urban_Open_Space_Map',
      region: AOI,
      crs: 'EPSG:4326',
      scale: 10,
      folder: 'Data_Mastery_Challenge',
      fileFormat: 'GeoTIFF',
      formatOptions: {
        noData: noDataVal
      }
    });
    
    // -----------------------------Export Confusion Matrix
    var exportTrainAccuracy = ee.Feature(null, {matrix: trainAccuracy.array()});
    Export.table.toDrive({
      collection: ee.FeatureCollection(exportTrainAccuracy),
      folder: 'Data_Mastery_Challenge',
      description: 'Confusion_Matrix',
      fileFormat: 'CSV'
    });
    
    return(imgClassified);
  
};
/*
USER INPUT:

User input can be changed in the RF_Classification function below:
  Change Area_Of_Interest: As exported from previous phase, i.e., Sentinel-2 Processing, Area_Of_Interest is imported from GEE Assets
  Change Sentinel2_Cloud_Free_Image: As exported from previous phase, Sentinel2_Cloud_Free_Image is imported from GEE Assets
  Change Land_Cover_Classifier_Vector_Points: Data from previous Sample Acquisition step is uploaded as GEE Assets, and input as Land_Cover_Classifier_Vector_Points
Sentinel 2 Classified Map and Confusion Matrix are exported in Drive for sharing; Navigate to Tasks panel on left and select Run

Run the code
*/
print(RF_Classification(Area_Of_Interest, Sentinel2_Cloud_Free_Image, Land_Cover_Classifier_Vector_Points));