import ee
import os
import rasterio
import cv2
import numpy as np
import matplotlib.pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/EarthEngineExports'
outputDir = '/content/drive/My Drive/ThematicMapsForUSEF'
os.makedirs(output_dir, exist_ok=True)


dataDir1 = '/content/drive/My Drive/Cropped_Maps'
outputDir1 = '/content/drive/My Drive/NDVI_Analysis'
os.makedirs(outputDir1, exist_ok=True)

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

def classify_ndvi_from_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    red_pixels = np.all(image_rgb == [165, 0, 38], axis=-1)
    yellow_pixels = np.all(image_rgb == [255, 255, 191], axis=-1)
    green_pixels = np.all(image_rgb == [0, 104, 55], axis=-1)
    return np.sum(red_pixels), np.sum(yellow_pixels), np.sum(green_pixels)

def load_images(start, end):
    red_counts = []
    yellow_counts = []
    green_counts = []
    tick_labels = []

    filenames = sorted([f for f in os.listdir(dataDir1) if f.endswith('.png')])
    for i in range(start, end):
        if i >= len(filenames):
            break

        filePath = os.path.join(dataDir1, filenames[i])
        image = cv2.imread(filePath)

        red_count, yellow_count, green_count = classify_ndvi_from_image(image)
        red_counts.append(red_count)
        yellow_counts.append(yellow_count)
        green_counts.append(green_count)

        month = i + 1
        tick_labels.append(f'Month {month}')

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
  
plt.figure(figsize=(18, 8))
    plt.plot(range(start + 1, end + 1), red_counts, label='Red (Low NDVI)', color='red', marker='o', linewidth=1)
    plt.plot(range(start + 1, end + 1), yellow_counts, label='Yellow (Moderate NDVI)', color='gold', marker='o', linewidth=1)
    plt.plot(range(start + 1, end + 1), green_counts, label='Green (High NDVI)', color='green', marker='o', linewidth=1)

    plt.xticks(ticks=range(start + 1, end + 1), labels=tick_labels, rotation=45)
    plt.xlabel('Image Index')
    plt.ylabel('Pixel Count')
    plt.title(f'NDVI Pixel Classification for Images {start + 1} to {end}')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()

    output_plot = os.path.join(outputDir1, f'NDVI_Trends_{start + 1}_to_{end}.png')
    plt.savefig(output_plot, dpi=300)
    plt.close()

total_images = len([f for f in os.listdir(dataDir1) if f.endswith('.png')])
for x in range(0, total_images, 12):
    load_images(x, x + 12)
