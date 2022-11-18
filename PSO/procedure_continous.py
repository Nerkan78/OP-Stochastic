import numpy as np

from Continous import ProblemContinuous
from utils import *
# from operators import *
from config import create_config, create_graph, create_times
from time import time
import pickle
from utils import sample_from_position
np.set_printoptions(formatter={'float': lambda x: "{0:0.3f}".format(x)})
import matplotlib.pyplot as plt

X_MIN = -20
X_MAX = 20
Y_MIN = -20
Y_MAX = 20

PROFIT_MIN = 10
PROFIT_MAX = 100

N_PARTICLES = 20
# T_MAX = 300

# EXPERIMENT_NAME = f'{N_NODES}_{T_MAX}_{N_SCENARIOS}'

T_SERVICE_MIN = 10
T_SERVICE_MAX = 100

N_SCENARIOS = 1
MODE = 'deterministic' if N_SCENARIOS == 1 else 'stochastic'

# Setup of graphs and scenarios
# for n_points in [10, 20, 30]:
#     create_graph(n_points, X_MIN, X_MAX, Y_MIN, Y_MAX, PROFIT_MIN, PROFIT_MAX, save_graph=f'data\\graph_{n_points}.pkl')
#     create_times(n_points, T_SERVICE_MIN, T_SERVICE_MAX, N_SCENARIOS, save_times=f'data\\times_{n_points}_{N_SCENARIOS}.pkl')


for n_points in [10]:
    for w in (0.5,):
        for t_max in (450,):
            for n_particles in (50,):
                for velocity_weight in (5e-2, ):
                    config = create_config(n_points=n_points,
                                           w=w,
                                           t_max=t_max,
                                           n_particles=n_particles,
                                           n_epoch=100,
                                           c1=0.6,
                                           c2 = 0.9,
                                           load_graph=f'data\\graph_{n_points}.pkl',
                                           load_times=f'data\\times_{n_points}_{N_SCENARIOS}.pkl',
                                           )

                    random_problem = ProblemContinuous(**config)
                    random_problem.create_population()

                    num_epoch = config['n_epoch']
                    history_profit = [deepcopy([]) for i in range(config['n_particles'])]
                    history_matrix = [deepcopy([]) for i in range(config['n_particles'])]
                    start_time = time()
                    print(f'velocity_weight = {velocity_weight}')
                    for epoch in range(num_epoch):
                        random_problem.update_population(velocity_weight, history_profit, history_matrix)
                        # print(random_problem.gbest)
                        # print(f' ITERATION {epoch}')

                    # print(f'---- GLOBAL BEST PROFIT {random_problem.gbest_profit} ----')
                    # print(f'---- GLOBAL BEST PATH SAMPLE {calculate_cost_profit(random_problem.gbest, random_problem.times, random_problem.profits, random_problem.T_max, random_problem.distance)[0]} ----')
                    # print(f'---- GLOBAL BEST MATRIX \n{random_problem.gbest} ----')

                    # print(random_problem.gbest_profit)

                    duration = time() - start_time
                    print(duration)
                    sample = sample_from_position(random_problem.gbest,
                                                  random_problem.profits,
                                                  random_problem.T_max,
                                                  random_problem.points_coordinates,
                                                  random_problem.times,
                                                  random_problem.mode,
                                                  random_problem.alpha)

                    print(f'sample best = {sample}')
                    np.savetxt(f'results\\history_profit_npoints={n_points}_w={w}_tmax={t_max}_nparticles={n_particles}_vweight={velocity_weight}.txt', np.array(history_profit))

                    with open (f'results\\history_matrix_npoints={n_points}_w={w}_tmax={t_max}_nparticles={n_particles}_vweight={velocity_weight}.pkl', 'wb') as f:
                        pickle.dump(np.array(history_matrix), f)

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



