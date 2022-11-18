from copy import deepcopy

import numpy as np


def distance(point1, point2, points):
    return np.linalg.norm(points[point1] - points[point2])


def empiric_function(x, path, times_distribution, num_samples = 200):
    prob = 0
    for k in range(num_samples):
        s = 0
        for node in path:
            s += np.random.choice(np.array(times_distribution[node])[:, 0], p=np.array(times_distribution[node])[:, 1])
        if s <= x:
            prob += 1
    return prob / num_samples


def extended_print(s):
    print(f'----- {s} -----')

def expected_time(time_distribution):
    try:
        return np.apply_along_axis(lambda x: x[0] * x[1], 1, time_distribution).sum()
    except:
        print(time_distribution)
        print(time_distribution.shape)
        raise


def position_cost(position, times, all_points):
    complete_path = [0] + position + [0]
    cost = 0
    for i, _ in enumerate(complete_path[:-1]):
        cost += distance(complete_path[i], complete_path[i+1], all_points)
        cost += expected_time(times[complete_path[i]])
    return cost


def check_cost(position, T_max, all_points, times, mode='deterministic', alpha=0.05):
    complete_path = [0] + position + [0]
    cost = 0
    for i, _ in enumerate(complete_path[:-1]):
        cost += distance(complete_path[i], complete_path[i + 1], all_points)
    if mode == 'deterministic':
        return cost + times[np.array(position)][:, 0, 0].sum() <= T_max
    elif mode == 'stochastic':
        violation_prob = 1 if cost >= T_max else 1 - empiric_function(T_max - cost, position, times)

        return violation_prob < alpha
    else:
        raise NotImplementedError


def position_profit(position, profits):
    return sum([profits[point] for point in position])


def normalize(position):
    if np.min(position) < 0 :
        position += abs(np.min(position))


    np.fill_diagonal(position, 0)
    position[:, 0] = 0

    maxes = np.max(position, axis=0)
    if (maxes > 1e-9).sum() == 1:
        position = np.where(position > 1e-9, 1, 0)
    else:
        position = position / position.sum(axis=1)[:, None]
    return position


def sample_from_position(position, profits, T_max, points_coordinates, times, mode, alpha):
    current_path = []
    point = 0
    profit = 0
    new_position = position.copy()
    while True:
        # print('loop 1')
        it = 0

        if max(new_position[point]) < 1e-5:
            break
        new_position[point] /= new_position[point].sum()
        point = np.random.choice(list(range(len(position))), p=new_position[point])

        # point = np.argmax(new_position[point])
        path_candidate = deepcopy(current_path)
        path_candidate.append(point)
        if check_cost(path_candidate, T_max, points_coordinates, times, mode, alpha):
            current_path = deepcopy(path_candidate)
            profit += profits[point]
        else:
            break
        if len(current_path) >= len(profits) - 1:
            break
        new_position[:, point] = 0
    return current_path, profit

def calculate_cost_profit(position, times, profits, points_coordinates, T_max,  mode, alpha):
    calculated_profits = []
    for num_sample in range(100):
        # print(num_sample)
        current_path, profit = sample_from_position(position, profits, T_max, points_coordinates, times, mode, alpha)
        calculated_profits.append(profit)
    return current_path, np.mean(calculated_profits)



