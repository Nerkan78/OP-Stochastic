from utils import *
from copy import deepcopy
import numpy as np
from time import time

def select_jpq_step2(W, path, travel_matrix, cost_matrix, expected_path_duration, expected_times, profits, teta_1, L, mode):
    min_eval = np.inf
    best_jpq = (None, None, None)
    for j in W:
        for index_p, p in enumerate(path[:-1]):
            q = path[index_p + 1]
            expected_change = expected_path_duration + travel_matrix[p][j] + travel_matrix[j][q] - travel_matrix[p][q] + expected_times[j]
            if expected_change <= L * (1 + teta_1):
                evaluation = cost_matrix[p][j] + cost_matrix[j][q] - cost_matrix[p][q] - profits[j]
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_jpq = (j, p, q)
    return best_jpq
    


def select_jpq_step5(W, path, travel_matrix, cost_matrix, expected_times,times_distribution, profits, L, alpha, num_samples, mode):
    min_eval = np.inf
    best_jpq = (None, None, None)
    initial_prob = calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution, L, num_samples = num_samples, mode=mode)
    # print(f'initial prob is {initial_prob}')
    for j in W:
        for index, (p, q) in enumerate(zip(path[:-1],path[1:])):
            
            start_time = time()
            
            evaluation = cost_matrix[p][j] + cost_matrix[j][q] - cost_matrix[p][q] - profits[j]
            if evaluation < min_eval:
                changed_path = deepcopy(path)
                changed_path.insert(index+1, j)
                new_prob = calculate_exceed_path_probability(changed_path, travel_matrix, expected_times, times_distribution, L, num_samples = num_samples, mode=mode)
                
                if new_prob <= alpha:
                    # print(f'new_prob is {new_prob}')
                    min_eval = evaluation
                    best_jpq = (j, p, q)

    if min_eval == np.inf:
        for j in W:
            for index, (p, q) in enumerate(zip(path[:-1],path[1:])):

                evaluation = cost_matrix[p][j] + cost_matrix[j][q] - cost_matrix[p][q]
                if evaluation < min_eval:
                    changed_path = deepcopy(path)
                    changed_path.insert(index+1, j)
                    new_prob = calculate_exceed_path_probability(changed_path, travel_matrix, expected_times, times_distribution, L, num_samples =num_samples, mode=mode)
                   
                    if new_prob <= alpha:
                        # print(f'new_prob is {new_prob}')
                        min_eval = evaluation
                        best_jpq = (j, p, q)

    return best_jpq    
    
    
def select_pijq_step6(W, path, cost_matrix, profits):
    max_eval = -np.inf
    best_pijq = (None, None, None, None)
    # print('start loop')
    for k in range(len(path) - 4):
        p, i, j, q = path[k:k+4]
        evaluation = cost_matrix[p][i] + cost_matrix[i][j] + cost_matrix[j][q] - cost_matrix[p][q] - profits[i] - profits[j]
        if evaluation > max_eval:
            max_eval = evaluation
            best_pijq = (p, i, j, q)
            # print('pijq is updated')
    
    return best_pijq



def select_ij_step7(W, path, cost_matrix, travel_matrix, expected_times, times_distribution, profits, L, alpha, num_samples, mode):
    best_eval = np.inf
    for index_i, i in enumerate(path):
        if i == 0:
            continue
        for j in W:
            prev_i = path[index_i - 1]
            next_i = path[index_i + 1]
            exchange_path = deepcopy(path)
            exchange_path[index_i] = j
            if calculate_exceed_path_probability(exchange_path, travel_matrix, expected_times, times_distribution, L, num_samples=num_samples, mode=mode) <= alpha:
                evaluation = cost_matrix[prev_i][i] + cost_matrix[i][next_i] + profits[j] - cost_matrix[prev_i][j] - cost_matrix[j][next_i] - profits[i]
                if evaluation > best_eval:
                    best_eval = evaluation
                    best_ij = i, j
    if best_eval == np.inf:
        return None, None
    return best_ij
            