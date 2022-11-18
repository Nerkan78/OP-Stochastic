import numpy as np
from scipy.spatial import distance_matrix
import pickle


def create_graph(n_points, x_min, x_max, y_min, y_max, profit_min, profit_max, save_graph=None):
    x_coordinates = np.random.uniform(x_min, x_max, n_points)
    y_coordinates = np.random.uniform(y_min, y_max, n_points)
    points_coordinates = np.vstack((x_coordinates, y_coordinates)).T
    profits = np.random.randint(profit_min, profit_max, n_points)
    profits[0] = 0
    travel_matrix = distance_matrix(points_coordinates, points_coordinates).tolist()
    graph_configuration = {'n_points': n_points,
                           'points_coordinates': points_coordinates,
                           'profits': profits,
                           'travel_matrix': travel_matrix}
    if save_graph:
        with open(save_graph, 'wb') as f:
            pickle.dump(graph_configuration, f)
    return graph_configuration


def create_times(n_points, t_service_min, t_service_max, n_scenarios, save_times=None):
    times = np.random.randint(t_service_min, t_service_max, (n_points, n_scenarios, 2)).astype(float)
    times[:, :, 1] = 1 / n_scenarios
    times[0, :, 0] = 0
    times_config = {'times': times}
    if save_times:
        with open(save_times, 'wb') as f:
            pickle.dump(times_config, f)
    return times_config


def create_solution(w, c1, c2, n_particles, n_epoch, save_solution=None):
    solution_config = {'w': w, 'c1': c1, 'c2': c2, 'n_particles': n_particles, 'n_epoch': n_epoch}
    if save_solution:
        with open(save_solution, 'wb') as f:
            pickle.dump(solution_config, f)

    return solution_config


def create_problem(t_max, mode, alpha, save_problem=None):
    problem_config = {'mode': mode, 'alpha': alpha, 't_max': t_max}
    if save_problem:
        with open(save_problem, 'wb') as f:
            pickle.dump(problem_config, f)

    return problem_config


def create_config(
        n_points=10, x_min=-10, x_max=10, y_min=-10, y_max=10, profit_min=2, profit_max=10,
        t_service_min=10, t_service_max=100, n_scenarios=1,
        w=0.3, c1=0.5, c2=0.5, n_particles=10, n_epoch=10,
        t_max=120, mode='deterministic', alpha=0.05,
        load_graph=None,
        load_times=None,
        load_solution=None,
        load_problem=None,
        load_config=None,
        save_graph=None,
        save_times=None,
        save_solution=None,
        save_problem=None,
        save_config=None
):
    if load_config:
        with open(load_config, 'rb') as f:
            config = pickle.load(f)
        return config
    
    config = {}
    graph_config = {}
    times_config = {}
    solution_config = {}
    problem_config = {}

    if load_graph:
        with open(load_graph, 'rb') as f:
            graph_config = pickle.load(f)
    else:
        graph_config = create_graph(n_points, x_min, x_max, y_min, y_max, profit_min, profit_max, save_graph)
    
    if load_times:
        with open(load_times, 'rb') as f:
            times_config = pickle.load(f)
    else:
        times_config = create_times(n_points, t_service_min, t_service_max, n_scenarios, save_times)
    
    if load_solution:
        with open(load_solution, 'rb') as f:
            solution_config = pickle.load(f)
    else:
        solution_config = create_solution(w, c1, c2, n_particles, n_epoch, save_solution)
    
    if load_problem:
        with open(load_problem, 'rb') as f:
            problem_config = pickle.load(f)
    else:
        problem_config = create_problem(t_max, mode, alpha, save_problem)
    
    config.update(graph_config)
    config.update(times_config)
    config.update(solution_config)
    config.update(problem_config)

    if save_config:
        with open(save_config, 'wb') as f:
            pickle.dump(config, f)
    return config






# for T_MAX in (300, 600, 900, 1200, 1500):
#     for N_SCENARIOS in (1, 2, 3, 4):
#         # N_SCENARIOS = 1
#         MODE = 'deterministic' if N_SCENARIOS == 1 else 'stochastic'
# 
#         X_MIN = -20
#         X_MAX = 20
#         Y_MIN = -20
#         Y_MAX = 20
# 
#         PROFIT_MIN = 10
#         PROFIT_MAX = 100
# 
#         N_PARTICLES = 20
#         # T_MAX = 300
# 
#         SAVE_PARAMETERS = True
#         SAVE_RESULTS = True
#         EXPERIMENT_NAME = f'{N_NODES}_{T_MAX}_{N_SCENARIOS}'
# 
#         T_SERVICE_MIN = 10
#         T_SERVICE_MAX = 100
# 
#         profits = np.random.randint(PROFIT_MIN, PROFIT_MAX, N_NODES)
#         profits[0] = 0
#         times = np.random.randint(T_SERVICE_MIN, T_SERVICE_MAX, (N_NODES, N_SCENARIOS, 2)).astype(float)
#         times[:, :, 1] = 1 / N_SCENARIOS
#         times[0, :, 0] = 0
# 
#         x_coordinates = np.random.uniform(X_MIN, X_MAX, N_NODES)
#         y_coordinates = np.random.uniform(Y_MIN, Y_MAX, N_NODES)
# 
#         points_coordinates = np.vstack((x_coordinates, y_coordinates)).T
# 
#         graph_configuration = {'n_nodes' : N_NODES, 'profits' : profits, 'times' : times, 'points_coordinates' : points_coordinates}
# 
#         problem_configuration =  { 'T_max' : T_MAX, 'mode' : MODE, 'alpha' : 0.05, 'n_scenarios' : N_SCENARIOS}
# 
#         solution_configuration = {'c1' : 0.5, 'c2' : 0.5, 'w' : 0.3, 'n_particles' : N_PARTICLES, 'PSO_num_epoch' : N_EPOCH, 'experiment_name' : EXPERIMENT_NAME, 'save_results' : SAVE_RESULTS }
# 
#         config = solution_configuration
#         config.update(graph_configuration)
#         config.update(problem_configuration)



        # if SAVE_PARAMETERS:
        # import pickle
        # from scipy.spatial import distance_matrix
        # with open(f'..\\experiments\\data\\times_{EXPERIMENT_NAME}.pkl', 'wb') as times_f,\
        #         open(f'..\\experiments\\data\\profits_{EXPERIMENT_NAME}.pkl', 'wb') as profits_f,\
        #         open(f'..\\experiments\\data\\travel_matrix_{EXPERIMENT_NAME}.pkl', 'wb') as travel_matrix_f,\
        #         open(f'..\\experiments\\data\\config_{EXPERIMENT_NAME}.pkl', 'wb') as config_f:
        #     pickle.dump(profits.tolist(), profits_f)
        #     pickle.dump(times, times_f)
        #     pickle.dump(distance_matrix(points_coordinates, points_coordinates).tolist(), travel_matrix_f)
        #     pickle.dump(config, config_f)
        #
        #
        # subprocess.call(['python', 'procedure.py', f'--config_path', f'..\\experiments\\data\\config_{EXPERIMENT_NAME}.pkl'], shell=True)

