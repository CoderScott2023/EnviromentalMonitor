import os
import tensorflow as tf

file_path = "NDVI_Pixel_Counts.txt"

data = []
with open(file_path, "r") as file:
    for line in file:
        line = line.strip()
        if line.startswith("Month"):
            current_month = int(line.split(" ")[1].strip(":"))
        elif line:
            category, count = line.split(":")
            data.append((current_month, category.strip(), int(count.strip())))
