import csv
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

data = pd.read_csv('drone specs.csv')
calcs = pd.DataFrame({'weight':pd.Series([(i*3*45)+300 for i in range(2,7)]),'ah':pd.Series([(i*2.6) for i in range(2,7)]),'$':pd.Series([(i*8+30) for i in range(2,7)])})
x = data['g'].to_numpy().reshape((-1, 1))
y = data['A'].to_numpy()
model = LinearRegression().fit(x,y)
nums = np.array([i for i in range(150,1000,10)])
preds = model.predict(nums.reshape((-1, 1)))
nd = pd.DataFrame({'A':preds,'g':nums})

times = {}
for thrtl in range(0,110,5):
    t = []
    for i in range(len(calcs['weight'])):
        amps = model.predict(np.array([(calcs['weight'][i]/4)*(1+(thrtl/100))]).reshape((-1, 1)))[0]
        t.append((calcs['ah'][i]/(amps*4))*60)
    times[f'{thrtl}'] = t

times = pd.DataFrame(times)
times.index = calcs['ah']/2.6
times = times.T
print(calcs)
costs = pd.DataFrame()
for i in times:
    costs[f'{i}'] = times[i]/calcs['$'][int(i)-2]
print(times)
print(costs)
plt.xlabel('% above hover')
plt.ylabel('flight time (mins)')
plt.plot(times)
plt.show()
#make equation for total weight -> flight time
