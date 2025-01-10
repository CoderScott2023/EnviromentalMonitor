import ee
import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/EarthEngineExports'
outputDir = '/content/drive/My Drive/ThematicMapsForUSEF'
os.makedirs(output_dir, exist_ok=True)

ee.Authenticate()
ee.Initialize(project="project-id") #not going to put my actual project id here for obvious reasons, especially cuz i wanna make this public sometime. Just know that it goes here for stuff like colab


landsat_5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA')
landsat_7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA')
landsat_8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')


wasatchFrontAreaBounding = ee.Geometry.Polygon([
  [-113, 40], [-113, 42],
  [-111, 42], [-111, 40]
])

images = landsat_8 \
    .filterDate('2000-01-01', '2020-01-01') \
    .filterBounds(wasatchFrontAreaBounding)

def getMedianImageOfMonth(year, month):
    startDate = f'{year}-{month:02d}-01'
    endDate = f'{year}-{month:02d}-30' if month != 2 else f'{year}-{month:02d}-28'
    monthlyImages = images.filterDate(startDate, endDate).mean()
    return monthlyImages

def createNDVImap(year, month):
    monthlyImages = getMedianImageOfMonth(year, month)
    ndvi = monthlyImages.normalizedDifference(["B5", "B4"])
    return ndvi

def classify_ndvi(ndviData):
    ndviClass = np.zeros_like(ndviData, dtype=np.uint8)
    ndviClass[ndviData > 0.6] = 3
    ndviClass[(ndviData > 0.2) & (ndviData <= 0.6)] = 2
    ndviClass[ndviData <= 0.2] = 1
    return ndviClass

for year in range(2000, 2021):
  if year == 2013 or year == 2014 or year == 2015:
    continue
    for month in range(1, 13):
        if year == 2016 and month != 12:
          continue
        ndviMap = createNDVImap(year, month)
        
        task = ee.batch.Export.image.toDrive(
            image=ndviMap.clip(wasatchFrontAreaBounding),
            description=f'NDVI_Year_{year}_Month_{month:02d}',
            folder='EarthEngineExports',
            scale=30,
            region=wasatchFrontAreaBounding.getInfo(),
            maxPixels=1e9
        )
      
        task.start()
  
for filename in sorted(os.listdir(dataDir)):
    if filename.endswith('.tif'):
        filePath = os.path.join(dataDir, filename)
        
        with rasterio.open(filePath) as src:
            ndviData = src.read(1)
            
        ndvi_class = classify_ndvi(ndviData)

        cmap = plt.cm.get_cmap('RdYlGn', 3)  # Red to Green colormap
        plt.figure(figsize=(10, 8))
        plt.imshow(ndvi_class, cmap=cmap, interpolation='nearest')
        plt.colorbar(ticks=[1, 2, 3], label='NDVI Classification')
        plt.title(f'NDVI Color Map - {filename}')
        plt.axis('off')
        
        output_file = os.path.join(output_dir, f'{filename.replace(".tif", ".png")}')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
