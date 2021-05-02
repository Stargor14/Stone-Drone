import csv
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

data = pd.read_csv('drone specs.csv')
x = data['%'].to_numpy().reshape((-1, 1))
y = data['g'].to_numpy()
model = LinearRegression().fit(x,y)
nums = np.array([i for i in range(30,100)])
preds = model.predict(nums.reshape((-1, 1)))
preds = preds.tolist()
for i in range(30):
    preds.insert(i,0)
x = data['g'].to_numpy().reshape((-1, 1))
y = data['A'].to_numpy()
model = LinearRegression().fit(x,y)
nums = np.array([i for i in range(150,1000)])
preds2 = model.predict(nums.reshape((-1, 1)))
preds2 = preds2.tolist()
for i in range(30):
    preds2.insert(i,0)
desired = int(input("Desired Total Thrust (g):"))

def predict(desired):
    possible = False
    for i in range(len(preds)-1):
        if preds[i] < desired/4 and preds[i+1] > desired/4:
            print(f'{i}% & {preds2[int(desired/4)]*4}A required to achieve desired thrust')
            return i,preds2[int(desired/4)]*4
            possible = True
    if not possible:
        return 0,0
print(predict(desired))
plt.plot(preds)
plt.show()
