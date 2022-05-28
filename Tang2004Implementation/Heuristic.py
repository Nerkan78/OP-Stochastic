
import numpy as np
from utils import *
from steps import *
import matplotlib.pyplot as plt
from time import time
import pandas as pd


def calculate_path(profits, 
                    cost_matrix, 
                    travel_matrix, 
                    times_distribution,
                    expected_times,
                    L, alpha, mode, 
                    num_samples):
    
    num_iterations = 100
    path = [0, 0]
    expected_path_duration = 0
    teta_1 = 0.01
    teta_2 = 0.01
    # alpha -= error
    
    
    print(num_samples)
    # num_samples = 1000
    path = [0, 0]
    expected_path_duration = 0
    start_time = time()
    # step 1
    W = create_W(travel_matrix, times_distribution, L, alpha)
    # print(f'W is created {W}')
    # step 2
    k = 0
    while len(W) > 0:
        j, p, q = select_jpq_step2(W, 
                                    path, 
                                    travel_matrix, 
                                    cost_matrix, 
                                    expected_path_duration, 
                                    expected_times, 
                                    profits, 
                                    teta_1, 
                                    L,
                                    mode)
        # print(f'iter is {k} j p q are {j}, {p}, {q} ')
        if j is None:
            break
        if len(np.unique(path)) == 1 or profits[j] > cost_matrix[p][j] + cost_matrix[j][q] - cost_matrix[p][q]:
            path, W = update_path(path, W, j, p ,q)
            # print(f'path is updated {path} W is {W}')
            expected_path_duration += travel_matrix[p][j] + travel_matrix[j][q] - travel_matrix[p][q] + expected_times[j]
        else:
            break

        k += 1
    print(f'path after step 2 {path}')
    # step 3
    # path = apply_Or_opt(path)
    # step 4
    # exceed_path_probability_markov = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, 'Markov')
    exceed_path_probability = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L,num_samples=num_samples, mode=mode)
    print(f'before step 6 {exceed_path_probability}')
    # assert round(exceed_path_probability * L, 2) == round(expected_path_duration, 2)
    # step 6
    while exceed_path_probability > alpha:
        p, i, j, q = select_pijq_step6(W, path, cost_matrix, profits)
        i_index = path.index(i)
        j_index = path.index(j)
        assert i_index != 0
        assert j_index != 0
        path.pop(i_index)
        path.pop(j_index)
        expected_path_duration -= travel_matrix[p][i] + travel_matrix[i][j]+ travel_matrix[j][q] - travel_matrix[p][q] + expected_times[i] + expected_times[j]
        exceed_path_probability = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L*(1 - teta_2), num_samples=num_samples, mode=mode)
        print(f'inside step 6 {exceed_path_probability}')
    # print(exceed_path_probability)
    # print(f'path after step 6 {path}')
    # step 5
    # print(f'before step 5 W is {W}')
    while len(W) > 0:
        # print(path)s
        j, p, q = select_jpq_step5(W, path, travel_matrix, cost_matrix, expected_times, times_distribution, profits, L, alpha,num_samples=num_samples, mode=mode)
        # print(j)
        if j is None:
            break
        if profits[j] > cost_matrix[p][j] + cost_matrix[j][q] - cost_matrix[p][q]:
            path, W = update_path(path, W, j, p ,q)
            expected_path_duration += travel_matrix[p][j] + travel_matrix[j][q] - travel_matrix[p][q] + expected_times[j]
        else:
            break
    print(f' after step 5 {calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, num_samples = num_samples, mode = mode)}')
    # print(f'path after step 5 {path}')       
    # step 7
    # assert calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, num_samples = num_samples) <= alpha + 0.005
    while len(W) > 0:
        i, j = select_ij_step7(W, path, cost_matrix, travel_matrix, expected_times, times_distribution, profits, L,  alpha,num_samples=num_samples, mode=mode)
        if i is not None:
            index_i = path.index(i)
            prev_i = path[index_i - 1]
            next_i = path[index_i + 1]
            path[index_i] = j_index
            expected_path_duration += travel_matrix[prev_i][i] + travel_matrix[i][next_i] + expected_times[j] - travel_matrix[prev_i][j] - travel_matrix[j][next_i] - expected_times[i]
        else:
            break
    taken_time = time() - start_time
    goal = sum([profits[node] for node in path])
    violation_prob = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, mode = 'empiric', num_samples=10000)
    expected_duration = sum(expected_times[node] for node in path) + sum([travel_matrix[node][next_node] for node, next_node in zip(path[:-1], path[1:])])

    # vs = []
    # for o in range(100):
        # violation_self = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, num_samples=num_samples, mode = mode)
        # vs.append(violation_self)


    # violations_self_mean = (vs[0])
    # violations_self_std = (np.std(vs))

    return path, round(taken_time, 3), round(goal, 3), round(violation_prob, 3), round(expected_duration, 3) #, round(violations_self_mean, 3), round(violations_self_std, 3)

# result_data = []
# for num_samples in range(100, 1100, 100):
    # path, taken_time, goal, violation_prob, expected_duration, violations_self_mean, violations_self_std = calculate_path(profits, 
                                                                                                                        # cost_matrix, 
                                                                                                                        # travel_matrix, 
                                                                                                                        # times_distribution,
                                                                                                                        # expected_times,
                                                                                                                        # L, alpha, 'empiric', 
                                                                                                                        # num_samples)
    # print(f'------------------\n Num samples {num_samples} \n {path} \n goal {goal}, violation_prob {violation_prob}, expected_duration {expected_duration}, violations_self_mean {violations_self_mean}, violations_self_std {violations_self_std} \n ----------------------')
    # result_data.append([goal, expected_duration, violation_prob, violations_self_mean, violations_self_std, taken_time])
# path, taken_time, goal, violation_prob, expected_duration, violations_self_mean, violations_self_std = calculate_path(profits, 
                                                                                                                        # cost_matrix, 
                                                                                                                        # travel_matrix, 
                                                                                                                        # times_distribution,
                                                                                                                        # expected_times,
                                                                                                                        # L, alpha, 'expected', 
                                                                                                                        # num_samples)
# print(f'------------------\n Expected \n {path} \n goal {goal}, violation_prob {violation_prob}, expected_duration {expected_duration}, violations_self_mean {violations_self_mean}, violations_self_std {violations_self_std} \n ----------------------')
    

# result_data.append([goal, expected_duration, violation_prob, violations_self_mean, violations_self_std, taken_time])    
    
# result_data = pd.DataFrame(np.array(result_data), index = [f'{num_samples}' for num_samples in range(100, 1100, 100)] + ['expected'], columns = ['Profit', 'Expect_dur', 'Viol_prob_exact', 'Viol_prob_heur', 'Viol_prob_heur_std', 'taken_time'])
# result_data.to_csv('results.csv', sep = ',')
# print(violations_self_mean)
# print(violations_self_std)
# fig, axes = plt.subplots(nrows=2, ncols=2, figsize = (30, 20))
# axes[0][0].plot(samples,times)
# axes[0][0].set_xlabel('Number of samples')
# axes[0][0].set_ylabel('Running time, s') 
# axes[0][0].set_title('Running time dependency') 

# axes[0][1].plot(samples,goals)
# axes[0][1].set_xlabel('Number of samples')
# axes[0][1].set_ylabel('Expected profit') 
# axes[0][1].set_title('Expected profit dependency') 

# axes[1][0].plot(samples,expected)
# axes[1][0].set_xlabel('Number of samples')
# axes[1][0].set_ylabel('Expected path time, s') 
# axes[1][0].set_title('Expected path dependency') 

# axes[1][1].plot(samples,violations_self_mean, label = 'self')
# axes[1][1].fill_between(samples, np.array(violations_self_mean) -  2*np.array(violations_self_std), np.array(violations_self_mean) +  2*np.array(violations_self_std), alpha=0.3)
# axes[1][1].plot(samples,violations_presize, label = 'accurate')
# axes[1][1].set_xlabel('Number of samples')
# axes[1][1].set_ylabel('Probabilty') 
# axes[1][1].set_title('Violation probability dependency') 
# axes[1][1].legend()

# fig.savefig('analysis.png', dpi=400)
    
# print_path_info(path, expected_times, L, times_distribution, travel_matrix, profits,num_samples=num_samples)
# print_path_info(list(range(20)) + [0], expected_times, L, times_distribution, travel_matrix, profits,num_samples=num_samples)   