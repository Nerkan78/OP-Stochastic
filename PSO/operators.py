import numpy as np
from copy import deepcopy
from utils import *


def theta_operator(p1, p2):
    velocity = []
    for point in p1:
        if point not in p2:
            velocity.append(point)
    # if isp1_gbest:
    #     priority = 'HP'
    # elif isp1_pbest:
    #     priority = 'LP'
    # else:
    #     priority = 'NP'
    return velocity


def mul_operator(c, v):
    new_velocity = []
    for point in v:
        if np.random.random() < c:
            new_velocity.append(point)
    return new_velocity


def add_operator(v1, v2, pr1, pr2):
    new_velocity = []
    v1 = deepcopy(v1)
    v2 = deepcopy(v2)
    if pr1 == 'HP' and pr2 == 'LP':
        high_priority = []
        for point in v1:
            if point in v2:
                new_velocity.append(point)
                v2.remove(point)
            else:
                high_priority.append(point)
        new_velocity += high_priority + v2
    elif pr1 == 'LP' and pr2 == 'HP':
        high_priority = []
        for point in v2:
            if point in v1:
                new_velocity.append(point)
                v1.remove(point)
            else:
                high_priority.append(point)
        new_velocity += high_priority + v1
    elif pr2 == 'NP':
        new_velocity += v1 + [point for point in v2 if point not in v1]
    elif pr1 == 'NP':
        new_velocity += v2 + [point for point in v1 if point not in v2]
    else:
        raise NotImplementedError(f'There is no condition for priorities {pr1} {pr2}')
    return new_velocity


def node_insert_increasing_profit(position, cost, new_point, profits, times, T_max, points_coordinates, mode, alpha):
    initial_cost = cost # position_cost(position, points_coordinates)
    complete_path = [0] + position + [0]
    distance_ = lambda p1, p2: distance(p1, p2, points_coordinates)

    best_cost = np.inf
    best_index = 'Not implemented'
    for insert_index in range(1, len(position)+1):
        cost_change = (
                distance_(new_point, complete_path[insert_index])
                + distance_(new_point, complete_path[insert_index - 1])
                - distance_(complete_path[insert_index], complete_path[insert_index-1])
        )
        cost_change += expected_time(times[new_point])
        if cost_change < best_cost:
            best_cost = cost_change
            best_index = insert_index

    new_position = deepcopy(position)
    new_position.insert(best_index-1, new_point)
    new_cost = initial_cost + best_cost

    # print(new_point)
    # print(best_index)
    # print(position)
    # print(new_position)
    # assert round(new_cost, 3) == round(position_cost(new_position, times, points_coordinates), 3), f'Cost are not equal {new_cost} {position_cost(new_position, points_coordinates)}'

    if not check_cost(new_position, T_max, points_coordinates, times, mode, alpha):
        complete_path = [0] + new_position + [0]
        best_cost = 0
        for remove_index in range(1, len(new_position) + 1):
            if profits[complete_path[remove_index]] > profits[new_point]:
                continue
            cost_change = (
                    distance_(complete_path[remove_index], complete_path[remove_index-1])
                    + distance_(complete_path[remove_index], complete_path[remove_index+ 1])
                    - distance_(complete_path[remove_index + 1], complete_path[remove_index - 1])
            )
            cost_change += expected_time(times[complete_path[remove_index]])
            if cost_change > best_cost:
                best_cost = cost_change
                best_index = remove_index

        try_position = deepcopy(new_position)
        try_position.remove(complete_path[best_index])
        if not check_cost(try_position, T_max, points_coordinates, times, mode, alpha):
            return position, initial_cost
        else:
            new_position.remove(complete_path[best_index])
            new_cost -= best_cost
    return new_position, new_cost


def insert_operator(position, cost, velocity, profits, times,  T_max, points_coordinates, mode, alpha):
    new_position = deepcopy(position)
    new_cost = cost
    for point in velocity:
        new_position, new_cost = node_insert_increasing_profit(new_position, new_cost, point, profits, times,  T_max, points_coordinates, mode, alpha)
    return new_position, new_cost






