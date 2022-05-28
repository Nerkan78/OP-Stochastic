import numpy as np


def Q_next_node(current_node, current_level, max_level, spent_time, time_limit, graph_data, penalty):
    travel_matrix, times_distributions, profits = graph_data
    
    if current_level > max_level:
        raise ValueError ('Current level of Q more than maximum')
    elif current_level == max_level:
        # s = 0
        # for t, p in times_distributions[current_node]:

            # if spent_time + t < time_limit:
                # s += profits[current_node] * p
            # else:
                # s = -np.inf
                # print(f'spent time is {spent_time} t is {t}')
                # print('infinity encountered')
                # break
        # return s
        return sum([profits[current_node] * p if spent_time + t < time_limit else (time_limit - spent_time - t) * penalty for t, p in times_distributions[current_node]])
    else:
        if spent_time >= time_limit:
            # raise ValueError('Spent time >= time limit')
            return (time_limit - spent_time) * penalty
        
        return np.max([sum([(profits[current_node] + Q_next_node(next_node, current_level+1, max_level, spent_time + t + travel_matrix[current_node][next_node], time_limit, graph_data, penalty))  * p  for t, p in times_distributions[current_node]]) for next_node in range(0, len(profits)) if next_node != current_node])
    