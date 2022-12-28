import os
from pathlib import Path

import numpy as np
import pandas as pd

from Continous import ProblemContinuous
# from Discrete import Problem
from Exact import Problem
from utils import *
# from operators import *
from config import create_config, create_graph, create_times, read_TOPTW_file, create_problem
from time import time
import pickle
from utils import sample_from_position
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
import matplotlib.pyplot as plt

N_SCENARIOS = 1
MODE = 'deterministic' if N_SCENARIOS == 1 else 'stochastic'

type = 'discrete'
results = []
dir_name = 'c_r_rc_100_100'
# for filename in os.listdir(f'data/TOPTW/{dir_name}'):
#     if filename != 'r109.txt':
#         continue
#     print(f'data/TOPTW/{dir_name}/{filename}')
#     dirpath = Path(f'data/TOPTW_PROCESSED/{dir_name}')
#     dirpath.mkdir(parents=True, exist_ok=True)
#     _, _, t_max = read_TOPTW_file(f'data/TOPTW/{dir_name}/{filename}',
#                                save_graph=f'data/TOPTW_PROCESSED/{dir_name}/graph_{filename}',
#                                save_times=f'data/TOPTW_PROCESSED/{dir_name}/times_{filename}')

# for n_points in [10, 20, 50]:
for c1 in (0.2, ):
    for c1 in (0.2, ):
        for w in (0.5,):
            for n_particles in (25,):
                for velocity_weight in (5e-2, ):
                    config = create_config(n_points=10,
                                           w=w,
                                           t_max=900,
                                           n_particles=n_particles,
                                           n_epoch=30,
                                           c1=0.3,
                                           c2 = 0.3,
                                           load_config=f'data/artificial/N_{10}_T_{900}.pkl',
                                           )
                    config['profits'] = config['profits'][1:]
                    config['times'] = config['times'][1:]
                    config['points_coordinates'] = config['points_coordinates'][1:]
                    config['travel_matrix'] = np.array(config['travel_matrix'])[1:, 1:]
                    config['n_points'] -= 1


                    if type =='discrete':
                        random_problem = Problem(**config)
                    elif type == 'continuous':
                        random_problem = ProblemContinuous(**config)

                    random_problem.create_population()

                    num_epoch = config['n_epoch']
                    history_profit = [deepcopy([]) for i in range(config['n_particles'])]
                    history_matrix = [deepcopy([]) for i in range(config['n_particles'])]
                    start_time = time()
                    print(f'velocity_weight = {velocity_weight}')
                    for epoch in range(num_epoch):
                        random_problem.update_population(velocity_weight, history_profit, history_matrix)
                        # extended_print(random_problem.gbest)
                        # print(f' ITERATION {epoch}')

                        # print(f'---- GLOBAL BEST PROFIT {random_problem.gbest_profit} ----')
                    # print(f'---- GLOBAL BEST PATH SAMPLE {calculate_cost_profit(random_problem.gbest, random_problem.times, random_problem.profits, random_problem.T_max, random_problem.distance)[0]} ----')
                    # print(f'---- GLOBAL BEST MATRIX \n{random_problem.gbest} ----')

                    # print(random_problem.gbest_profit)

                    duration = time() - start_time
                    print(duration)
                    results.append([config['n_points'], t_max, duration, random_problem.gbest_profit])
                    if type == 'continuous':
                        sample = sample_from_position(random_problem.gbest,
                                                      random_problem.profits,
                                                      random_problem.T_max,
                                                      random_problem.points_coordinates,
                                                      random_problem.times,
                                                      random_problem.mode,
                                                      random_problem.alpha)

                        print(f'sample best = {sample}')
                    dirpath = Path(f'results/artificial/N_{n_points}_T_{t_max}')
                    dirpath.mkdir(parents=True, exist_ok=True)
                    print(random_problem.gbest)
                    print(random_problem.gbest_profit)
                    np.savetxt(Path(dirpath, 'history_profit.txt'), np.array(history_profit))
                    # [96, 93, 85, 16, 86, 44, 100, 59, 94, 95, 97, 87, 13]
                    # 299.0
                    #
                    # with open (f'results\\history_matrix_npoints={n_points}_w={w}_tmax={t_max}_nparticles={n_particles}_vweight={velocity_weight}.pkl', 'wb') as f:
                    #     pickle.dump(np.array(history_matrix), f)

                    # fig, axes = plt.subplots(ncols=3, figsize=(16, 8))
                    #
                    # for h in history_profit:
                    #     axes[0].plot(h)
                    #     #         axes[i][0].set_yticks(list(range(300, 600, 20)))
                    #     axes[0].set_title(f'Profit weight={velocity_weight}')
                    # # Optimal value
                    # # axes[i][0].axhline(424, xmin=0, xmax=30, linestyle='-.')
                    # for h in history_matrix:
                    #     coef = [(hmatrix * (1 - hmatrix)).sum() for hmatrix in h]
                    #     diff = [np.linalg.norm(diff_matrix) for diff_matrix in np.diff(h)]
                    #     axes[1].plot(coef)
                    #     #         axes[i][0].set_yticks(list(range(400, 500, 20)))
                    #     axes[1].set_title(f'Matrix coefficients  weight={velocity_weight}')
                    #     axes[2].plot(diff)
                    #     #         axes[i][0].set_yticks(list(range(400, 500, 20)))
                    #     axes[2].set_title(f'Matrix difference  weight={velocity_weight}')
                    # plt.savefig('graphics.png')
                    # plt.show()
df = pd.DataFrame(results, columns=['N', 'T max', 'duration', 'profit'])
df.to_csv('results/artificial/results.csv')

    #



#
# random_problem = Problem_con(**config)
# random_problem.create_population()
#
# print('---CONTINOUS---')
#
# num_epoch = 10
# history = [[] for i in range(config['n_particles'])]
# for epoch in range(num_epoch):
#     random_problem.update_population(history)
#     # print(random_problem.gbest)
#     print(f' ITERARTION {epoch}')
#     print(f'---- GLOBAL BEST PROFIT {random_problem.gbest_profit} ----')
#     print(f'---- GLOBAL BEST PATH SAMPLE {calculate_cost_profit(random_problem.gbest, random_problem.times, random_problem.profits, random_problem.T_max, random_problem.distance)[0]} ----')
#     # print(f'---- GLOBAL BEST MATRIX \n{random_problem.gbest} ----')
#
#     # print(random_problem.gbest_profit)
#
# duration = time() - start_time
# print(duration)
#
# np.savetxt('history.txt', np.array(history))



