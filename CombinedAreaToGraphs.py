import os
import ee
import rasterio
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.stats import linregress
from google.colab import drive

ee.Authenticate()
ee.Initialize(project="project-id")

landsat_5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_TOA')
landsat_7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_TOA')
landsat_8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')

wasatchFrontAreaBounding = ee.Geometry.Polygon([
    [-113, 40], [-113, 42],
    [-111, 42], [-111, 40]
])

images = landsat_8.filterDate('2000-01-01', '2020-01-01').filterBounds(wasatchFrontAreaBounding)

def getMedianImageOfMonth(year, month):
    startDate = f'{year}-{month:02d}-01'
    endDate = f'{year}-{month:02d}-30' if month != 2 else f'{year}-{month:02d}-28'
    monthlyImages = images.filterDate(startDate, endDate).mean()
    return monthlyImages

def createNDVImap(year, month):
    monthlyImages = getMedianImageOfMonth(year, month)
    ndvi = monthlyImages.normalizedDifference(["B5", "B4"])
    return ndvi

for year in range(2000, 2021):
    if year in [2013, 2014, 2015]:
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

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/EarthEngineExports'
outputDir = '/content/drive/My Drive/ThematicMapsForUSEF'
os.makedirs(outputDir, exist_ok=True)

def classify_ndvi(ndviData):
    ndviClass = np.zeros_like(ndviData, dtype=np.uint8)
    ndviClass[ndviData > 0.6] = 3
    ndviClass[(ndviData > 0.2) & (ndviData <= 0.6)] = 2
    ndviClass[ndviData <= 0.2] = 1
    return ndviClass

for filename in sorted(os.listdir(dataDir)):
    if filename.endswith('.tif'):
        filePath = os.path.join(dataDir, filename)
        
        with rasterio.open(filePath) as src:
            ndviData = src.read(1)
            
        ndvi_class = classify_ndvi(ndviData)
        cmap = plt.cm.get_cmap('RdYlGn', 3)
        plt.figure(figsize=(10, 8))
        plt.imshow(ndvi_class, cmap=cmap, interpolation='nearest')
        plt.colorbar(ticks=[1, 2, 3], label='NDVI Classification')
        plt.title(f'NDVI Color Map - {filename}')
        plt.axis('off')
        
        output_file = os.path.join(outputDir, f'{filename.replace(".tif", ".png")}')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

dataDir = '/content/drive/My Drive/NDVI_Maps'
outputDir = '/content/drive/My Drive/Cropped_Maps'
os.makedirs(outputDir, exist_ok=True)

y_start, y_end = 85, -50
x_start, x_end = 50, -350

for filename in os.listdir(dataDir):
    if filename.endswith('.png') or filename.endswith('.jpg'):
        input_path = os.path.join(dataDir, filename)
        output_path = os.path.join(outputDir, f"Cropped_{filename}")

        image = cv2.imread(input_path)
        if image is None:
            continue

        cropped_image = image[y_start:y_end, x_start:x_end]
        cv2.imwrite(output_path, cropped_image)

dataDir = '/content/drive/My Drive/Cropped_Maps'
outputDir = '/content/drive/My Drive/NDVI_Analysis2'
os.makedirs(outputDir, exist_ok=True)

def classify_ndvi_from_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    red_pixels = np.all(image_rgb == [165, 0, 38], axis=-1)
    yellow_pixels = np.all(image_rgb == [255, 255, 191], axis=-1)
    green_pixels = np.all(image_rgb == [0, 104, 55], axis=-1)
    return np.sum(red_pixels), np.sum(yellow_pixels), np.sum(green_pixels)

pre_2013, post_2013 = [], []
filenames = sorted([f for f in os.listdir(dataDir) if f.endswith('.png')])
for filename in filenames:
    if any(f'Year_{year}' in filename for year in range(2000, 2013)):
        pre_2013.append(filename)
    else:
        post_2013.append(filename)

def process_images(image_list, start_year):
    red_counts, yellow_counts, green_counts = [], [], []
    indices = list(range(1, len(image_list) + 1))

    for filename in image_list:
        filePath = os.path.join(dataDir, filename)
        image = cv2.imread(filePath)
        red_count, yellow_count, green_count = classify_ndvi_from_image(image)
        red_counts.append(red_count)
        yellow_counts.append(yellow_count)
        green_counts.append(green_count)

    plt.figure(figsize=(18, 8))
    plt.plot(indices, red_counts, label='Red (Low NDVI)', color='red', marker='o', linewidth=1)
    plt.plot(indices, yellow_counts, label='Yellow (Moderate NDVI)', color='gold', marker='o', linewidth=1)
    plt.plot(indices, green_counts, label='Green (High NDVI)', color='green', marker='o', linewidth=1)
    
    def add_trendline(x, y, color, label):
        slope, intercept, _, _, _ = linregress(x, y)
        plt.plot(x, slope * np.array(x) + intercept, color=color, linestyle='--', label=f'{label} Trend')
    
    add_trendline(indices, red_counts, 'darkred', 'Red (Low NDVI)')
    add_trendline(indices, yellow_counts, 'goldenrod', 'Yellow (Moderate NDVI)')
    add_trendline(indices, green_counts, 'darkgreen', 'Green (High NDVI)')

    plt.xlabel('Image Index')
    plt.ylabel('Pixel Count')
    plt.title(f'NDVI Pixel Classification ({start_year} Range)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    output_plot = os.path.join(outputDir, f'NDVI_Trends_{start_year}.png')
    plt.savefig(output_plot, dpi=300)
    plt.show()

if pre_2013:
    process_images(pre_2013, "Pre-2013")
if post_2013:
    process_images(post_2013, "Post-2013")
