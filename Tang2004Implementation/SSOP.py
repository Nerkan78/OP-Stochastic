import numpy as np
from utils import *
from steps import *
import matplotlib.pyplot as plt
from time import time
import pandas as pd
from Heuristic import *
import pickle 

result_data = []

for alpha in (1e-5, 0.05):

    for number_scenarios in range(1, 9):
        profits, cost_matrix, travel_matrix, times_distribution = read_input(number_scenarios, 20, 5)
        np.savetxt('profits.txt', profits)
        np.savetxt('travel_matrix.txt', travel_matrix)

        with open("../DominantApproach/profits.pkl","wb") as f:
            pickle.dump([float(p) for p in profits],f)
        with open(f'../DominantApproach/times_distribution_{number_scenarios}.pkl', 'wb') as f:
            pickle.dump(times_distribution,f)   
        with open(f'../DominantApproach/travel_matrix.pkl', 'wb') as f:
            pickle.dump([[float(travel_matrix[i][j]) for i in range(len(travel_matrix))] for j in range(len(travel_matrix))],f)
            

        # print(list(map(len, times_distribution)))
        # np.savetxt('times_distribution.txt', times_distribution)
        expected_times = calculate_expectations(times_distribution)
        L = 120
        num_samples = 1000
        path, taken_time, goal, violation_prob, expected_duration = calculate_path(profits, 
                                                                                    cost_matrix, 
                                                                                    travel_matrix, 
                                                                                    times_distribution,
                                                                                    expected_times,
                                                                                    L, alpha, 'empiric', 
                                                                                    num_samples)
        is_feasible = sum([max(times_distribution[node], key = lambda x: x[0])[0] for node in path]) + sum([travel_matrix[node][next_node] for node, next_node in zip(path[:-1],path[1:])]) <= L
        with open(f'../DominantApproach/path_{number_scenarios}.pkl', 'wb') as f:
            pickle.dump(path,f)
        result_data.append(['Heuristic', alpha, number_scenarios, goal, taken_time, violation_prob, expected_duration, is_feasible])
        # print(taken_time)
        # print(goal)
        # print(violation_prob)
        # print(expected_duration)
result_data = pd.DataFrame(np.array(result_data), columns = ['Algorithm', 'Alpha', 'Number_scenarios', 'goal', 'taken_time', 'violation_probability', 'expected_duration', 'is_feasible'])
result_data.to_csv('results.csv', sep = ';')
# expected_times = calculate_expectations(times_distribution)
# current_node = 0
# path = [0]
# graph_data = (travel_matrix, times_distribution, profits)
# time_limit = 120
# spent_time = 0
# all_nodes = list(range(20))
# visited_nodes = []
# gain = 0
# start_time = time()
# times = []
# exceeds = []
# for penalty in (10, 100, 1000, 10000, 100000, 200000, 1000000):
    # time_limit = 120
    # spent_time = 0
    # all_nodes = list(range(20))
    # visited_nodes = []
    # gain = 0
    # start_time = time()
    # times = []
    # current_node = 0
    # path = [0]
    # while True:

        # Q_best_value = 0
        # print(current_node)
        # start_loop_time = time()
        # for node in set(all_nodes).difference(set(path)):
            # time_travel = travel_matrix[current_node][node]
            # Q_value = Q_next_node(node, 0, 2, spent_time + time_travel, time_limit, graph_data, penalty)
            # print(f' for node {node} Q is {Q_value}')
            # if Q_value > Q_best_value:
                # best_next_node = node
                # Q_best_value = Q_value
        # end_loop_time = time()
        # times.append(end_loop_time - start_loop_time)
        # if Q_best_value == 0:
            # break
        # else:
            # taken_time = np.random.choice(a = [v for v, p in times_distribution[current_node]], p=[p for v, p in times_distribution[current_node]])
            # spent_time += travel_matrix[current_node][best_next_node] + taken_time
            # gain += profits[current_node]
            # current_node = best_next_node
            # path.append(current_node)
    # print(gain)
    # print(path)
    # exceed_prob = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, 120,num_samples=10000, mode='empiric')
    # print(exceed_prob)
    # exceeds.append(exceed_prob)
    # print(spent_time)
    # print(times)
    # print(time() - start_time)
    
# with open('exceeds.npy', 'wb') as outfile:
    # np.save(outfile, np.array(exceeds))
    
# plt.figure(figsize = (15, 15))
# plt.plot(np.log10([10, 100, 1000, 10000, 100000, 200000, 1000000]), exceeds)

# plt.savefig('exceeds.png', dpi=300)





    
    

