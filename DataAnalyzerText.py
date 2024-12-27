import os
import numpy as np
import cv2
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

def load_images_to_text(start, end, output_file):
    filenames = sorted([f for f in os.listdir(dataDir) if f.endswith('.png')])

    with open(output_file, 'a') as file:
        for i in range(start, end):
            if i >= len(filenames):
                break

            filePath = os.path.join(dataDir, filenames[i])
            image = cv2.imread(filePath)

            red_count, yellow_count, green_count = classify_ndvi_from_image(image)
            month = i + 1

            file.write(f"Month {month}:\n")
            file.write(f"Green: {green_count}\n")
            file.write(f"Yellow: {yellow_count}\n")
            file.write(f"Red: {red_count}\n")
            file.write("\n")
          
total_images = len([f for f in os.listdir(dataDir) if f.endswith('.png')])
output_text_file = os.path.join(outputDir, "NDVI_Pixel_Counts.txt")

if os.path.exists(output_text_file):
    open(output_text_file, 'w').close()

for x in range(0, total_images, 12):
    load_images_to_text(x, x + 12, output_text_file)

print(f"NDVI pixel counts have been saved to: {output_text_file}")
