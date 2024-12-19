import cv2
import matplotlib.pyplot as plt
from google.colab import drive

dataDir = '/content/drive/My Drive/NDVI_Maps'
outputDir = '/content/drive/My Drive/Cropped_Maps'

k = 0

for x in range(k):
    image_path = "NDVI_Year_2001_Month_12.png"
    image = cv2.imread(image_path)

    y_start = 85
    y_end = -50
    x_start = 50
    x_end = -350

    cropped_image = image[y_start:y_end, x_start:x_end]

    plt.imshow(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    plt.show()

output_path = "Cropped_NDVI_Map.png"
cv2.imwrite(output_path, cropped_image)
