import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.stats import linregress
from google.colab import drive

drive.mount('/content/drive')

dataDir = '/content/drive/My Drive/Cropped_Maps'
outputDir = '/content/drive/My Drive/NDVI_Analysis2'
os.makedirs(outputDir, exist_ok=True)
def classify_ndvi_from_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    red_pixels = np.all(image_rgb == [165, 0, 38], axis=-1)
    yellow_pixels = np.all(image_rgb == [255, 255, 191], axis=-1)
    green_pixels = np.all(image_rgb == [0, 104, 55], axis=-1)
    return np.sum(red_pixels), np.sum(yellow_pixels), np.sum(green_pixels)
pre_2013 = []
post_2013 = []

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
