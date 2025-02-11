import matplotlib.pyplot as plt

years = list(range(2000, 2014))
tempsPre = [30.5, 31.2, 29.8, 32.1, 30.7, 31.0, 31.5, 32.0, 29.2, 30.0, 
         30.8, 29.6, 33.4, 31.7]
tempsPost = [32.8, 33.1, 33.0, 32.9, 33.2, 31.0, 32.5]

plt.figure(figsize=(10, 5))
plt.plot(years, tempsPre, marker='o', linestyle='-', color='b', label="Avg January Temp (°F)")

plt.xlabel("Year")
plt.ylabel("Average Temperature (F)")
plt.title("Average January Temperatures (2000-2013) in Wasatch Front")
plt.xticks(np.arange(2000, 2015, 2))
plt.grid(True)
plt.legend()

plt.show()

years = list(range(2014, 2021))

plt.figure(figsize=(10, 5))
plt.plot(years, tempsPost, marker='o', linestyle='-', color='b', label="Avg January Temp (°F)")

plt.xlabel("Year")
plt.ylabel("Average Temperature (F)")
plt.title("Average January Temperatures (2014-2020) in Wasatch Front")
plt.xticks(np.arange(2014, 2021, 2))
plt.grid(True)
plt.legend()

plt.show()
