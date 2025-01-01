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
organized_data = {}
for month, category, count in data:
    if month not in organized_data:
        organized_data[month] = {"Green": 0, "Yellow": 0, "Red": 0}
    organized_data[month][category] = count
