import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/Cropped_Maps'
outputDir = '/content/drive/My Drive/NDVI_Analysis'
os.makedirs(outputDir, exist_ok=True)

def classify_ndvi_from_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    red_pixels = np.all(image_rgb == [255, 0, 0], axis=-1)
    yellow_pixels = np.all(image_rgb == [255, 255, 0], axis=-1)
    green_pixels = np.all(image_rgb == [0, 128, 0], axis=-1)

    red_count = np.sum(red_pixels)
    yellow_count = np.sum(yellow_pixels)
    green_count = np.sum(green_pixels)

    return red_count, yellow_count, green_count

months = []
red_counts = []
yellow_counts = []
green_counts = []

for filename in sorted(os.listdir(dataDir)):
    if filename.endswith('.png'):
        month = filename.split('_')[-1].replace('.png', '')
        months.append(month)

        filePath = os.path.join(dataDir, filename)
        image = cv2.imread(filePath)

        red_count, yellow_count, green_count = classify_ndvi_from_image(image)
        red_counts.append(red_count)
        yellow_counts.append(yellow_count)
        green_counts.append(green_count)

plt.figure(figsize=(12, 6))
plt.plot(months, red_counts, label='Red (Low NDVI)', color='red', marker='o')
plt.plot(months, yellow_counts, label='Yellow (Moderate NDVI)', color='gold', marker='o')
plt.plot(months, green_counts, label='Green (High NDVI)', color='green', marker='o')
plt.xlabel('Month')
plt.ylabel('Pixel Count')
plt.title('NDVI Pixel Classification Over Time')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()

output_plot = os.path.join(outputDir, 'NDVI_Trends.png')
plt.savefig(output_plot, dpi=300)
plt.show()
