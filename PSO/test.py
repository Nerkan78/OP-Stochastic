import pickle
from copy import deepcopy
from time import time
from joblib import Parallel, delayed
import numpy as np

from utils import normalize, check_cost, position_profit

# np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})



with open(f'data\\graph_10.pkl', 'rb') as f:
    graph_config = pickle.load(f)
with open(f'data\\times_10_1.pkl', 'rb') as f:
    times_config = pickle.load(f)

n_points = graph_config['n_points']
all_points = graph_config['points_coordinates']
profits = graph_config['profits']
times = times_config['times']
T_max = 450



current_first = 1
def solve(current_path, point_candidate):
    candidate_path = deepcopy(current_path) + [point_candidate]
    if check_cost(candidate_path, T_max, all_points, times, mode='deterministic', alpha=0.05):
        current_path = deepcopy(candidate_path)
        if len(current_path) == 9:
            return position_profit(current_path, profits), current_path
        return max((solve(current_path, point) for point in range(1, 10) if point not in current_path), key=lambda x:x[0])
    else:
        global current_first
        if current_first == current_path[0]:
            print(current_path)
            current_first += 1
        return position_profit(current_path, profits), current_path
    return NotImplementedError


# print(max((solve([], point) for point in range(1, 10)), key=lambda x:x[0]))
#
# print(profits)
# 600 : (530, [2, 3, 4, 7, 6, 9, 8])
# 450 : (424, [6, 7, 3, 4, 5, 8])

# position = np.random.random((n_points, n_points))
# print((position * (1-position)).sum())
#
# one_position = np.zeros((n_points, n_points))
# for i in range(10):
#     one_position[i][(i+1) % 10] = 1
# print(one_position)
# print((one_position * (1-one_position)).sum())

start_time = time()


def sqrt(i):
    s = 0
    for j in range(10000):
        s += 1
    return i

result = sum(Parallel(n_jobs=4)(delayed(sqrt)(i) for i in range(10000)))
print(result)
print(time() - start_time)


start_time = time()




result = sum(sqrt(i) for i in range(10000))
print(result)
print(time() - start_time)