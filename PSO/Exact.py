import numpy as np
from joblib import Parallel, delayed

from utils import position_profit, extended_print, distance, check_cost
from operators import *
from copy import deepcopy

'''
Here we present solution as matrix Y, where Y_ij denotes whether on step i node j was added
We can squeeze it into vector y, where Y_ij = y_ni+j  
'''



class Particle:
    def __init__(self, position, id, problem):
        self.position = position
        self.pbest = position
        self.id = id
        self.problem = problem


        self.cost = np.inf if position @ self.problem.C @ position + self.problem.t @ position - self.problem.T_max >= 0 else 0
        self.profit = self.problem.p @ self.position - self.cost
        self.pbest_profit = self.problem.p @ self.position - self.cost

    def evaluate(self):
        current_profit = self.problem.p @ self.position - self.cost
        # if self.id == 1:
        #     extended_print(self.position)
        if current_profit > self.pbest_profit:
            self.pbest = self.position
            self.pbest_profit = current_profit
            # print('LOCAL UPDATE')
        self.profit = current_profit
        return self

    def gradient_descent(self):
        L = self.problem.T_max
        C = self.problem.C
        t = self.problem.t
        p = self.problem.p
        epsilon = self.problem.epsilon

        lambda_ = 0
        v = np.zeros(len(self.position))
        delta = np.inf
        y = self.position
        while delta > 1e-5:
            dy = -y + np.clip(y - (-p + lambda_ * (2 * C @ y + t) + (2 * np.diag(y) - np.eye(len(y))) @ v), 0, 1)
            dlambda = -lambda_ + np.clip(lambda_ + y @ C @ y + t @ y - L, 0, None)
            dv = y * (y-1)
            delta = max([np.linalg.norm(dy), abs(dlambda), np.linalg.norm(dv)])
            print(f'y is {y}')
            print(f'dy is {dy}')
            print(f'lambda_ is {lambda_}')
            print(f'dlambda is {dlambda}')
            print(f'v is {v}')
            print(f'dv is {dv}')

            print(f'delta is {delta}')
            print(f'-----------')
            y -= dy * epsilon
            lambda_ -= dlambda * epsilon
            v -= dv * epsilon
        return y

    def update(self, verbose=0):
        r1 = np.random.random()
        r2 = np.random.random()

        position_converged = self.gradient_descent()
        local_update = self.problem.c1 * r1 * (self.pbest - self.position)
        global_update = self.problem.c2 * r2 * (self.problem.gbest - self.position)
        inertia = self.problem.w * (position_converged - self.position)

        if verbose > 1:
            print(f'LOCAL UPDATE \n {local_update}')
            print(f'GLOBAL UPDATE \n {global_update}')
            print(f'INERTIA \n {inertia}')
        new_position = self.position + inertia + local_update + global_update

        if verbose > 0:
            print(f'PREVIOUS POSITION \n {self.position}')
            print(f'NEW POSITION \n {new_position}')

        self.position = new_position
        self.cost = np.inf if y @ self.problem.C @ y + self.problem.t @ y - self.problem.T_max >= 0 else 0
        return self






class Problem:
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
        self.travel_matrix = kwargs['travel_matrix']

        n = self.n_points
        self.t = np.repeat([expected_time(time_distribution) for time_distribution in self.times], n)
        self.C = np.block([[np.zeros((n, n)) if j != i+1 else self.travel_matrix for j in range(n)] for i in range(n)])
        self.p = np.repeat(profits, n)
        self.epsilon = 1e-5

    def create_population(self):
        for i in range(self.n_particles):
            # position = np.random.random(self.n_points ** 2)
            position = np.zeros(self.n_points ** 2)
            # print(f'Created position {position}')
            self.particles.append(Particle(
                position, i, self)
            )

        self.gbest_profit = -np.inf
        for particle in self.particles:
            if particle.pbest_profit > self.gbest_profit:
                self.gbest_profit = particle.pbest_profit
                self.gbest = particle.position

    def update_population(self, velocity_weight, history_profit, history_matrix):
        for i, particle in enumerate(self.particles):
            particle.update()
            # particle_cost = position_cost(particle.position, self.points_coordinates)
            # assert particle_cost <= self.T_max, f'Constraint breach {particle_cost}'
            particle.evaluate()
            history_profit[i].append(particle.profit)
            # print(f'---- PARTICLE {i} ----')
            # print(f'POSITION { particle.position} ----')
            # print(f'VELOCITY { particle.velocity} ----')
            # print(f'BEST POSITION { particle.pbest} ----')
            # print(f'BEST PROFIT { particle.pbest_profit} ----')

        for particle in self.particles:
            if particle.pbest_profit > self.gbest_profit:
                self.gbest_profit = particle.pbest_profit
                self.gbest = particle.position