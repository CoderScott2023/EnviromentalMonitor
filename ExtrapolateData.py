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

months = []
green_counts = []
yellow_counts = []
red_counts = []

for month, counts in organized_data.items():
    months.append(month)
    green_counts.append(counts["Green"])
    yellow_counts.append(counts["Yellow"])
    red_counts.append(counts["Red"])

green_norm = green_counts / green_counts.max()
yellow_norm = yellow_counts / yellow_counts.max()
red_norm = red_counts / red_counts.max()

y = green_norm[1:]
X = np.stack([green_norm[:-1], yellow_norm[:-1], red_norm[:-1]], axis=1)

split_index = int(len(X) * 0.9)
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

model = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

