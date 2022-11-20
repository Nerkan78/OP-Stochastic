import numpy as np
from utils import position_profit, extended_print, distance, check_cost
from operators import *
from copy import deepcopy


class Particle:
    def __init__(self, position, velocity, cost, profit, n_points, mode, alpha, id):
        self.position = position
        self.velocity = velocity
        self.pbest = position
        self.pbest_profit = profit
        self.profit = profit
        self.n_points = n_points
        self.cost = cost
        self.mode = mode
        self.alpha = alpha
        self.id = id

    def evaluate(self, profits):
        current_profit = position_profit(self.position, profits)
        # if self.id == 1:
        #     extended_print(self.position)
        if current_profit > self.pbest_profit:
            self.pbest = self.position
            self.pbest_profit = current_profit
            # print('LOCAL UPDATE')
        self.profit = current_profit

    def update(self, weight, c1, c2, gbest, profits, times, T_max, points_coordinates, velocity_weight):

        local_update = theta_operator(self.pbest, self.position)
        local_update = mul_operator(c1, local_update)

        global_update = theta_operator(gbest, self.position)
        global_update = mul_operator(c2, global_update)

        update = add_operator(local_update, global_update, 'LP', 'HP')
        inertia = mul_operator(weight, self.velocity)

        new_velocity = add_operator(inertia, update, 'NP', 'NP')

        new_position, new_cost = insert_operator(self.position, self.cost, new_velocity, profits, times, T_max, points_coordinates, self.mode, self.alpha)
        # if self.id == 0:
        #     extended_print('')
        #     extended_print(f' T MAX {T_max}')
        #     extended_print(f'OLD POSITION {self.position}')
        #     extended_print(f'OLD COST {self.cost}')
        #     extended_print(f'VELOCITY {new_velocity}')
        #     extended_print(f'NEW POSITION {new_position}')
        #     extended_print(f'NEW COST {new_cost}')
        #     extended_print('')

        control_list = list(range(1, self.n_points))
        np.random.shuffle(control_list)
        new_velocity = theta_operator(control_list, new_position)

        self.position = new_position
        self.velocity = new_velocity
        self.cost = new_cost






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
            cost = position_cost(position, self.times, all_points=self.points_coordinates)
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

    def update_population(self, velocity_weight, history_profit, history_matrix):
        for i, particle in enumerate(self.particles):
            particle.update(self.w, self.c1, self.c2, self.gbest, self.profits, self.times, self.T_max, self.points_coordinates, velocity_weight)
            # particle_cost = position_cost(particle.position, self.points_coordinates)
            # assert particle_cost <= self.T_max, f'Constraint breach {particle_cost}'
            particle.evaluate(self.profits)
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