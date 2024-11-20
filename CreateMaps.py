import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/EarthEngineExports'
outputDir = '/content/drive/My Drive/ThematicMapsForUSEF'
os.makedirs(output_dir, exist_ok=True)

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

        cmap = plt.cm.get_cmap('RdYlGn', 3)  # Red to Green colormap
        plt.figure(figsize=(10, 8))
        plt.imshow(ndvi_class, cmap=cmap, interpolation='nearest')
        plt.colorbar(ticks=[1, 2, 3], label='NDVI Classification')
        plt.title(f'NDVI Color Map - {filename}')
        plt.axis('off')
        
        output_file = os.path.join(output_dir, f'{filename.replace(".tif", ".png")}')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
