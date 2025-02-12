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

years = list(range(2000, 2021))
temps = [30.5, 31.2, 29.8, 32.1, 30.7, 31.0, 31.5, 32.0, 29.2, 30.0, 
         30.8, 29.6, 33.4, 31.7, 32.8, 33.1, 33.0, 32.9, 33.2, 31.0, 32.5]

def classify_ndvi_from_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    red_pixels = np.all(image_rgb == [165, 0, 38], axis=-1)
    yellow_pixels = np.all(image_rgb == [255, 255, 191], axis=-1)
    green_pixels = np.all(image_rgb == [0, 104, 55], axis=-1)
    return np.sum(red_pixels), np.sum(yellow_pixels), np.sum(green_pixels)

filenames = sorted([f for f in os.listdir(dataDir) if f.endswith('.png')])

ndvi_data = {year: None for year in years}

for filename in filenames:
    for year in years:
        if f'Year_{year}' in filename and 'Month_01' in filename:
            filePath = os.path.join(dataDir, filename)
            image = cv2.imread(filePath)
            ndvi_data[year] = classify_ndvi_from_image(image)

years = [year for year in years if ndvi_data[year] is not None]
temps = temps[:len(years)]
red_counts, yellow_counts, green_counts = zip(*[ndvi_data[year] for year in years])

fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.set_xlabel("Year")
ax1.set_ylabel("Average Temperature (F)", color='b')
ax1.plot(years, temps, marker='o', linestyle='-', color='b', label="Avg January Temp")
ax1.tick_params(axis='y', labelcolor='b')

ax2 = ax1.twinx()
ax2.set_ylabel("NDVI Pixel Count", color='g')
ax2.plot(years, red_counts, marker='o', linestyle='-', color='red', label="Low NDVI (Red)")
ax2.plot(years, yellow_counts, marker='o', linestyle='-', color='gold', label="Moderate NDVI (Yellow)")
ax2.plot(years, green_counts, marker='o', linestyle='-', color='green', label="High NDVI (Green)")
ax2.tick_params(axis='y', labelcolor='g')

def add_trendline(ax, x, y, color, label):
    slope, intercept, _, _, _ = linregress(x, y)
    ax.plot(x, slope * np.array(x) + intercept, color=color, linestyle='--', label=f'{label} Trend')

add_trendline(ax1, years, temps, 'darkblue', "Temperature")
add_trendline(ax2, years, red_counts, 'darkred', "Low NDVI")
add_trendline(ax2, years, yellow_counts, 'goldenrod', "Moderate NDVI")
add_trendline(ax2, years, green_counts, 'darkgreen', "High NDVI")

plt.title("January Temperature & NDVI Trends (2000-2020) - Wasatch Front")
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.xticks(np.arange(2000,2021,2))

output_plot = os.path.join(outputDir, 'Combined_Temp_NDVI_Trends_January.png')
plt.savefig(output_plot, dpi=300)
plt.show()
