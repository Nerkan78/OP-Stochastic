from time import time
from utils import *
import numpy as np
import matplotlib.pyplot as plt

# times = []
# for k in range(2, 20):
    
    # profits, cost_matrix, travel_matrix, times_distribution = read_input(k)
    # path = list(range(k)) + [0]
    # L = 1000
    # expected_times = calculate_expectations(times_distribution)
    # start_time = time()
    # exceed_path_probability = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, 'exact')
    # exec_time = time() - start_time
    # print(exec_time)
    # times.append(exec_time)
 
# plt.figure(figsize = (20, 12))
# plt.plot(list(range(2, 20)), times)
# plt.xlabel('number of nodes')
# plt.ylabel('time in seconds')
# plt.savefig('ProbTimeDependency')

def empiric_function(x, path,  num_samples = 1000):
    prob = 0
    for k in range(num_samples):
        s = 0
        for node in path:
            s += np.random.choice(np.array(times_distribution[node])[:, 0], p=np.array(times_distribution[node])[:, 1])
        if s <= x:
            prob += 1
    return prob / num_samples

def calculate_from(start, path, L):
    if start == len(path) - 1:
        return 1 if L < 0 else 0
    else:
        return sum([p * calculate_from(start + 1, path, L - value) for value, p in times_distribution[path[start]]])

N = 6
times_distribution = ([[[v, 1 / 4] for v in (30, 60, 90, 120)] for n in range(N)])
times_distribution[0] = [[0, 1]]
print(times_distribution)

path = list(range(N)) + [0]
L = 900

# prob = calculate_from(0, path, L)
# print(prob)
print(1 - empiric_function(L, path))
print(np.random.choice([1,2,3]))