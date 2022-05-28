import sys
import pandas as pd
import numpy as np
import pickle


data = pd.read_csv('../module_time.csv', delimiter = ';', header = None, names = ['mo_id', 'un_id', 'dur'])
profits_data = pd.read_csv('../module_universe.csv', delimiter = ';', header = None, names = ['mo_id', 'un_id'])
np.random.seed(seed=1)
mapping = {theme : np.random.randint(1, 5) for theme in profits_data.un_id.unique()}
profits = [0] + list(profits_data.un_id.map(mapping).values)
print(profits)

N = 20

for number_scenarios in list(range(1, 9)):
    times_distribution = [[[0, 1]]]
    bins = np.linspace(3, 15, number_scenarios + 1)
    for i in range(N-1):
        times = data[data['mo_id'] == i+1].values[:, 2]
        values, edges = np.histogram(times, bins = number_scenarios, range = (2, 15))
        mean_values = [np.mean(times[(edges[j] <= times) & (times <= edges[j+1])]) for j in range(len(edges)-1) ]
        times_distribution.append([[float(v),float(p)] for p, v in zip(values / sum(values), mean_values)])


        
    with open(f'../DominantApproach/19_times_{number_scenarios}.pkl', 'wb') as f:
        # for dist in times_distribution:
            # print(dist, file=f)
        pickle.dump(times_distribution,f)
        print(type(times_distribution))
with open(f'../DominantApproach/times_{number_scenarios}.pkl', 'rb') as f:
    # for dist in times_distribution:
        # print(dist, file=f)
    a = pickle.load(f)
    print(a)
    print(type(a))        
    ls = [type(item) for item in a]
    print(ls)
    
a = [[[0, 1]], [[1, 0.5], [2, 0.5]]]
with open("../DominantApproach/a.pkl","wb") as f:
    pickle.dump(a,f)