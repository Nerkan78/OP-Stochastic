import numpy as np
from utils import *
from operators import *
# from config import config, EXPERIMENT_NAME, SAVE_RESULTS
from time import time
import pickle
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config_path', type=str, help='Path to config file')      # option that takes a value

args = parser.parse_args()

class Particle:
    def __init__(self, position, velocity, cost, profit, n_points, mode, alpha, id):
        self.position = position
        self.velocity = velocity
        self.pbest = position
        self.pbest_profit = profit
        self.n_points = n_points
        self.cost = cost
        self.mode = mode
        self.alpha = alpha
        self.id = id

    def evaluate(self, profits):
        current_profit = position_profit(self.position, profits)
        if self.id == 1:
            extended_print(self.position)
        if current_profit > self.pbest_profit:
            self.pbest = self.position
            self.pbest_profit = current_profit
            # print('LOCAL UPDATE')

    def update(self, weight, c1, c2, gbest, profits, times, T_max, points_coordinates):

        local_update = theta_operator(self.pbest, self.position)
        local_update = mul_operator(c1, local_update)

        global_update = theta_operator(gbest, self.position)
        global_update = mul_operator(c2, global_update)

        update = add_operator(local_update, global_update, 'LP', 'HP')
        inertia = mul_operator(weight, self.velocity)

        new_velocity = add_operator(inertia, update, 'NP', 'NP')

        new_position, new_cost = insert_operator(self.position, self.cost, new_velocity, profits, times, T_max, points_coordinates, self.mode, self.alpha)

        control_list = list(range(1, self.n_points))
        np.random.shuffle(control_list)
        new_velocity = theta_operator(control_list, new_position)

        self.position = new_position
        self.velocity = new_velocity
        self.cost = new_cost






class Problem:
    def __init__(self, points_coordinates, profits, T_max, c1, c2, w, n_particles, times, **kwargs):
        self.points_coordinates = np.array(points_coordinates)
        self.T_max = T_max
        self.n_points = len(points_coordinates)
        self.distance = lambda p1, p2: distance(p1, p2, self.points_coordinates)
        self.particles = []
        self.profits = profits
        self.c1 = c1
        self.c2 = c2
        self.w = w
        self.gbest = []
        self.gbest_profit = 0
        self.n_particles = n_particles
        self.times = times
        self.mode = kwargs['mode']
        self.alpha = kwargs['alpha']

    def create_population(self):
        for i in range(self.n_particles):
            control_list = list(range(1, self.n_points))
            np.random.shuffle(control_list)
            position = []
            prev_point = 0
            cost = 0
            for index, point in enumerate(control_list):
                # cost += (
                #         self.distance(prev_point,point)
                #         + self.distance(point, 0)
                #         - self.distance(prev_point, 0)
                # )
                # cost += self.times[point]
                # if cost <= self.T_max:
                #     position.append(point)
                #     prev_point = point
                # else:
                #     cost -= (
                #         self.distance(prev_point,point)
                #         + self.distance(point, 0)
                #         - self.distance(prev_point, 0)
                # )
                #     cost -= self.times[point]
                #     break
                new_position = deepcopy(position)
                new_position.append(point)
                if check_cost(new_position, self.T_max, self.points_coordinates, self.times):
                    position = deepcopy(new_position)
                else:
                    break

            velocity = control_list[index:]
            # print(f'Created position {position}')
            self.particles.append(Particle(
                position, velocity, cost, position_profit(position, self.profits), self.n_points, self.mode, self.alpha, i)
            )

            self.gbest = position
            self.gbest_profit = position_profit(position, self.profits)
            for particle in self.particles:
                if particle.pbest_profit > self.gbest_profit:
                    self.gbest_profit = particle.pbest_profit
                    self.gbest = particle.position

    def update_population(self):
        for i, particle in enumerate(self.particles):
            particle.update(self.w, self.c1, self.c2, self.gbest, self.profits, self.times, self.T_max, self.points_coordinates)
            # particle_cost = position_cost(particle.position, self.points_coordinates)
            # assert particle_cost <= self.T_max, f'Constraint breach {particle_cost}'
            particle.evaluate(self.profits)
            # print(f'---- PARTICLE {i} ----')
            # print(f'POSITION { particle.position} ----')
            # print(f'VELOCITY { particle.velocity} ----')
            # print(f'BEST POSITION { particle.pbest} ----')
            # print(f'BEST PROFIT { particle.pbest_profit} ----')

        for particle in self.particles:
            if particle.pbest_profit > self.gbest_profit:
                self.gbest_profit = particle.pbest_profit
                self.gbest = particle.position



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


