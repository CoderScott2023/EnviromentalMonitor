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
    red_pixels = np.all(image_rgb == [165, 0, 38], axis=-1)
    yellow_pixels = np.all(image_rgb == [255, 255, 191], axis=-1)
    green_pixels = np.all(image_rgb == [0, 104, 55], axis=-1)
    return np.sum(red_pixels), np.sum(yellow_pixels), np.sum(green_pixels)

start_index = 1
end_index = 12

red_counts = []
yellow_counts = []
green_counts = []
tick_labels = []

filenames = sorted([f for f in os.listdir(dataDir) if f.endswith('.png')])
for i in range(start_index - 1, end_index):
    filePath = os.path.join(dataDir, filenames[i])
    image = cv2.imread(filePath)

    red_count, yellow_count, green_count = classify_ndvi_from_image(image)
    red_counts.append(red_count)
    yellow_counts.append(yellow_count)
    green_counts.append(green_count)

    month = i + 1
    tick_labels.append(f'Month {month}')

plt.figure(figsize=(18, 8))
plt.plot(range(start_index, end_index + 1), red_counts, label='Red (Low NDVI)', color='red', marker='o', linewidth=1)
plt.plot(range(start_index, end_index + 1), yellow_counts, label='Yellow (Moderate NDVI)', color='gold', marker='o', linewidth=1)
plt.plot(range(start_index, end_index + 1), green_counts, label='Green (High NDVI)', color='green', marker='o', linewidth=1)

plt.xticks(ticks=range(start_index, end_index + 1), labels=tick_labels, rotation=45)
plt.xlabel('Image Index')
plt.ylabel('Pixel Count')
plt.title('NDVI Pixel Classification Over Selected Range')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()

output_plot = os.path.join(outputDir, f'NDVI_Trends_{start_index}_to_{end_index}.png')
plt.savefig(output_plot, dpi=300)
plt.show()
