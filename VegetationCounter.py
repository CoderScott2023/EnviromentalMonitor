import cv2
import os
from matplotlib import pyplot as plt
from google.colab import drive

drive.mount('/content/drive')

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
        print(f"Saved cropped image to {output_path}")

        plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        plt.show()
