import numpy as np
from utils import *
from operators import *
# from config import config, EXPERIMENT_NAME, SAVE_RESULTS
from time import time
import pickle
import argparse
from Discrete import Particle, Problem


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config_path', type=str, help='Path to config file')      # option that takes a value

args = parser.parse_args()





print(args.config_path)
with open(args.config_path, 'rb') as f:
    config = pickle.load(f)

SAVE_RESULTS = config['save_results']
EXPERIMENT_NAME = config['experiment_name']
start_time = time()

random_problem = Problem(**config)
random_problem.create_population()

num_epoch = config['PSO_num_epoch']
for epoch in range(num_epoch):
    random_problem.update_population()
    print(random_problem.gbest)
    print(f' ITERATION {epoch}')
    print(f'---- GLOBAL BEST PROFIT {random_problem.gbest_profit} ----')
    print(f'---- GLOBAL BEST POSITION {random_problem.gbest} ----')
    # print(f'---- GLOBAL BEST COST {position_cost(random_problem.gbest, config["times"], config["points_coordinates"])} ----')

    print(random_problem.gbest_profit)

duration = time() - start_time
print(duration)
if SAVE_RESULTS:
    with open(f'..\\experiments\\results\\execution_time_{EXPERIMENT_NAME}.pkl', 'wb') as exec_time_f,\
        open(f'..\\experiments\\results\\best_path_{EXPERIMENT_NAME}.pkl', 'wb') as path_f,\
        open(f'..\\experiments\\results\\best_profit_{EXPERIMENT_NAME}.pkl', 'wb') as profit_f,\
        open(f'..\\experiments\\results\\best_cost_{EXPERIMENT_NAME}.pkl', 'wb') as cost_f:
        pickle.dump(duration, exec_time_f)
        pickle.dump(random_problem.gbest, path_f)
        pickle.dump(random_problem.gbest_profit, profit_f)
        pickle.dump(position_cost(random_problem.gbest, config["times"], config["points_coordinates"]), cost_f)


