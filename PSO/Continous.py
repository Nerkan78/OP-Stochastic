from copy import deepcopy

import numpy as np
from joblib import Parallel, delayed

from utils import calculate_cost_profit, normalize, distance


class ParticleContinuous:
    def __init__(self, position, velocity, profit, n_points):
        self.position = position
        self.velocity = velocity
        self.pbest = position
        self.pbest_profit = profit
        self.n_points = n_points
        self.profit = profit

    def evaluate(self, times, profits, points_coordinates, T_max, mode, alpha):
        _, current_profit = calculate_cost_profit(self.position, times, profits, points_coordinates, T_max, mode, alpha)
        self.profit = current_profit
        if current_profit > self.pbest_profit:
            self.pbest = self.position
            self.pbest_profit = current_profit
            # print('LOCAL UPDATE')
        return self

    def update(self, w, c1, c2, velocity_weight, gbest, verbose=0):
        r1 = np.random.random()
        r2 = np.random.random()

        local_update = c1 * r1 * (self.pbest - self.position)
        global_update = c2 * r2 * (gbest - self.position)
        inertia = w * self.velocity
        if verbose > 1:
            print(f'LOCAL UPDATE \n {local_update}')
            print(f'GLOBAL UPDATE \n {global_update}')
            print(f'INERTIA \n {inertia}')
        new_velocity = inertia + local_update + global_update
        new_velocity = normalize(new_velocity)
        new_position = normalize(velocity_weight * new_velocity + self.position)
        # new_cost = calculate_cost(new_position)

        if verbose > 0:
            print(f'PREVIOUS POSITION \n {self.position}')
            print(f'NEW POSITION \n {new_position}')

        self.position = new_position
        self.velocity = new_velocity
        # self.cost = new_cost
        return self


class ProblemContinuous:
    def __init__(self, points_coordinates, profits, t_max, c1, c2, w, n_particles, times, **kwargs):
        self.points_coordinates = np.array(points_coordinates)
        self.T_max = t_max
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
            position = np.random.random((self.n_points, self.n_points))
            # position = np.zeros((self.n_points, self.n_points))
            # for i in range(self.n_points):
            #     while True:
            #         next_point = np.random.randint(0, self.n_points)
            #         if next_point not in (0, i):
            #             position[i][next_point] = 1
            #             break

            position = normalize(position)
            _, profit = calculate_cost_profit(position, self.times, self.profits, self.points_coordinates, self.T_max, self.mode, self.alpha)
            velocity = np.random.random((self.n_points, self.n_points))
            velocity = normalize(velocity)

            self.particles.append(ParticleContinuous(
                position, velocity, profit, self.n_points)
            )

        self.gbest = self.particles[-1].position
        self.gbest_profit = self.particles[-1].pbest_profit
        for particle in self.particles:
            if particle.pbest_profit > self.gbest_profit:
                self.gbest_profit = particle.pbest_profit
                self.gbest = particle.position

    def update_population(self, velocity_weight, history_profit, history_matrix):
        new_particles = Parallel(n_jobs=20)(delayed(lambda x: x.update(self.w, self.c1, self.c2, velocity_weight,  deepcopy(self.gbest), 0))
                                           (particle) for particle in self.particles)
        # print(new_particles)
        new_particles = Parallel(n_jobs=20)(
            delayed(lambda x: x.evaluate(deepcopy(self.times), deepcopy(self.profits), deepcopy(self.points_coordinates), self.T_max, self.mode, self.alpha))(particle) for particle in new_particles)
        self.particles = new_particles
        for i, particle in enumerate(self.particles):
            # particle.update(self.w, self.c1, self.c2, velocity_weight,  self.gbest, 0)
            # particle_cost = position_cost(particle.position, self.points_coordinates)
            # assert particle_cost <= self.T_max, f'Constraint breach {particle_cost}'
            # particle.evaluate(self.times, self.profits, self.points_coordinates, self.T_max, self.mode, self.alpha)
            # if i == 1:
            #     print(f'---- PARTICLE {i} ----')
            #     print(f'  {"     ".join(np.arange(0, self.n_points, 1).astype(str))} \n{particle.position}')

            # print(f'VELOCITY { particle.velocity} ----')
            # print(f'BEST POSITION { particle.pbest} ----')
            # print(f'BEST PROFIT { particle.pbest_profit} ----')
            history_profit[i].append(particle.profit)
            history_matrix[i].append(particle.position)

        for particle in self.particles:
            if particle.pbest_profit > self.gbest_profit:
                self.gbest_profit = particle.pbest_profit
                self.gbest = particle.pbest