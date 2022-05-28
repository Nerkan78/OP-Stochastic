import numpy as np
import pandas as pd
import os

def read_input(number_scenarios, N = 20, travel_factor=5):
    '''
    times distribution - 3d array of shape (nodes, len(distribuion), 2),
       
                  contains value with probability of time in node
    '''
    data = pd.read_csv('../module_time.csv', delimiter = ';', header = None, names = ['mo_id', 'un_id', 'dur'])
    profits_data = pd.read_csv('../module_universe.csv', delimiter = ';', header = None, names = ['mo_id', 'un_id'])
    np.random.seed(seed=1)
    mapping = {theme : np.random.randint(1, 5) for theme in profits_data.un_id.unique()}
    profits = [0] + list(profits_data.un_id.map(mapping).values)
    print(profits)
    times_distribution = [[[0, 1]]]
    # bins = list(range(5, 35, 5))
    # number_scenarios = 4
    # N = 6
    for i in range(N-1):
        times = data[data['mo_id'] == i+1].values[:, 2]
        values, edges = np.histogram(times, bins = number_scenarios, range = (2, 15))
        mean_values = [np.mean(times[(edges[j] <= times) & (times <= edges[j+1])]) for j in range(len(edges)-1) ]
        times_distribution.append([[float(v),float(p)] for p, v in zip(values / sum(values), mean_values)])
    # times_distribution = np.array(times_distribution)
    travel_matrix = np.random.rand(N, N) * travel_factor
    travel_matrix = np.tril(travel_matrix) + np.tril(travel_matrix, -1).T
    np.fill_diagonal(travel_matrix, 0)
    cost_matrix = np.zeros((N, N))
    # profits = np.random.randint(1, 5, N)
    # profits[0] = 0
    # times_distribution = [[[v, 1 / 4] for v in (30, 60, 90, 120)] for n in range(N)]
    # times_distribution[0] = [[0, 1]]
    return profits, cost_matrix, travel_matrix, times_distribution

def calculate_expectations(times_distribution):
    expected_times = []
    for distribuion in times_distribution:
        expected_times.append(sum((value[0] * value[1] for value in distribuion)))
    return expected_times

def construct_accurate_empiric_function(path, times_distribution, num_samples = 10000, domain_size = 360, domain_min = 0, domian_max = 360):
    domain = np.linspace(domain_min, domian_max, domain_size)
    values = [empiric_function(x, path, times_distribution, num_samples) for x in domain]
    return domain, values

def empiric_function(x, path, times_distribution, num_samples = 200):
    prob = 0
    for k in range(num_samples):
        s = 0
        for node in path:
            s += np.random.choice(np.array(times_distribution[node])[:, 0], p=np.array(times_distribution[node])[:, 1])
        if s <= x:
            prob += 1
    return prob / num_samples

def calculate_exceed_path_probability(path, 
                                      travel_matrix, 
                                      expected_times, 
                                      times_distribution,  
                                      L,
                                      mode='expected',
                                      num_samples = 1000,
                                      domain_name='domain.npy', 
                                      values_name='values.npy'):
    
    travel_time = sum([travel_matrix[node][next_node] for node, next_node in zip(path[:-1],path[1:])])
    # use exact
    if mode == 'exact':
        def calculate_from(start, path, L):

            if start == len(path) - 1:
                return 1 if L < 0 else 0
            else:
                return sum([p * calculate_from(start + 1, path, L - value) for value, p in times_distribution[path[start]]])
        prob = calculate_from(0, path, L - travel_time)
    # Use Markov inequaluty    
    elif mode == 'Markov':
        prob = (sum([expected_times[node] for node in path]) + travel_time) / L
    elif mode == 'empiric':
        prob = (1 - empiric_function(L - travel_time, path, times_distribution, num_samples))
    elif mode == 'preconstructed':
        assert domain_name in os.listdir('.') and values_name in os.listdir('.'), 'provide files with domain and values of preconstructed empiric function'
        with open(domain_name, 'rb') as f:
            domain = np.load(f, allow_pickle=True)
        with open('values.npy', 'rb') as f:
            values = np.load(f, allow_pickle=True)
        
        index = np.where(domain > L - travel_time)[0][0]
        prev_index = index - 1
        spade = (L - travel_time - domain[prev_index]) / (domain[index] - domain[prev_index])
        prob = values[prev_index] + spade * (values[index] - values[prev_index])
    elif mode == 'expected':
        prob = 1 if sum([expected_times[node] for node in path]) >= L - travel_time else 0
    else:
        raise NotImplementedError
       
    return prob


def create_W(travel_matrix, times_distribution, L, alpha):
    node_Count = len(times_distribution)
    m = len(times_distribution[0])
    W = []
    for j in range(1, node_Count):
        if travel_matrix[0][j] + travel_matrix[j][0]  <= L and \
            sum((times_distribution[j][k][1] for k in range(m) if times_distribution[j][k][0] > L - travel_matrix[0][j] - travel_matrix[j][0] )) <= alpha:
            W.append(j)
    return W
    
def print_path_info(path, expected_times, L, times_distribution, travel_matrix, profits, num_samples=200):
    print(f'Path is {path}')
    print(f'Total profit of path {sum([profits[node] for node in path])}')
    travel_time = sum([travel_matrix[node][next_node] for node, next_node in zip(path[:-1],path[1:])])
    print(f'Expected time {travel_time + sum([expected_times[node] for node in path])}')
    print(f'Violation probability {calculate_exceed_path_probability(path, travel_matrix, expected_times, times_distribution,  L, num_samples=num_samples)}')
    
    
    



def update_path(path, W, j, p ,q):
    p_index = 0 if p == 0 else path.index(p)
    path.insert(p_index + 1, j)
    W.pop(W.index(j))
    return path, W


    
    

    
