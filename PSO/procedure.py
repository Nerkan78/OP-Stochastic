import os
from pathlib import Path

import numpy as np
import pandas as pd

from Continous import ProblemContinuous
from Discrete import Problem
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
for filename in os.listdir(f'data/TOPTW/{dir_name}'):
    if filename != 'r109.txt':
        continue
    print(f'data/TOPTW/{dir_name}/{filename}')
    dirpath = Path(f'data/TOPTW_PROCESSED/{dir_name}')
    dirpath.mkdir(parents=True, exist_ok=True)
    _, _, t_max = read_TOPTW_file(f'data/TOPTW/{dir_name}/{filename}',
                               save_graph=f'data/TOPTW_PROCESSED/{dir_name}/graph_{filename}',
                               save_times=f'data/TOPTW_PROCESSED/{dir_name}/times_{filename}')

    for n_points in [10]:
        for w in (0.5,):
            # for t_max in (450,):
            for _ in (1, ):
                for n_particles in (25,):
                    for velocity_weight in (5e-2, ):
                        config = create_config(n_points=n_points,
                                               w=w,
                                               t_max=t_max,
                                               n_particles=n_particles,
                                               n_epoch=30,
                                               c1=0.3,
                                               c2 = 0.3,
                                               load_graph=f'data/TOPTW_PROCESSED/{dir_name}/graph_{filename}',
                                               load_times=f'data/TOPTW_PROCESSED/{dir_name}/times_{filename}',
                                               )
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
                        results.append([f'{filename}', config['n_points'], t_max, duration, random_problem.gbest_profit])
                        if type == 'continuous':
                            sample = sample_from_position(random_problem.gbest,
                                                          random_problem.profits,
                                                          random_problem.T_max,
                                                          random_problem.points_coordinates,
                                                          random_problem.times,
                                                          random_problem.mode,
                                                          random_problem.alpha)

                            print(f'sample best = {sample}')
                        dirpath = Path(f'results/TOPTW_PROCESSED/{dir_name}')
                        dirpath.mkdir(parents=True, exist_ok=True)
                        print(random_problem.gbest)
                        np.savetxt(Path(dirpath, 'history_profit.txt'), np.array(history_profit))
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
df = pd.DataFrame(results, columns=['name', 'N', 'T max', 'duration', 'profit'])
df.to_csv('results/TOPTW_PROCESSED/results.csv')

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



