import pandas as pd
from matplotlib import pyplot as plt


plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True
headers = ['x', 'y']
df = pd.read_csv("data.csv", usecols=headers)
print("Contents in csv file:\n", df)
plt.plot(df.x, df.y)
print(df.x)
plt.show()