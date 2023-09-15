import sys
import os
import collections
import random

sys.path.insert(0, '../bomberman')

from entity import CharacterEntity
from sensed_world import SensedWorld, Event
from utility_scenario_one import Util
from utility_q import Util_Q

ALPHA = 0.2
GAMMA = 0.9

class QCharacter(CharacterEntity):
    weights = list()
    waiting_for_expl = False

    def __init__(self, name, avatar, x, y, weights, weights_file_name, epsilon):
        CharacterEntity.__init__(self, name, avatar, x, y)
        self.weights = weights
        self.functions = (Util_Q.exit_distance_q, Util_Q.monster_distance_q, Util_Q.closest_wall_below_distance_q)
        self.weights_file_name = weights_file_name
        self.epsilon = epsilon

    def best(self, wrld):
        '''
        Returns the (x, y) location of the world exit

                Parameters:
                        wrld (world): The world

                Returns:
                        (best_a, best_n, best_q) (tuple, tuple number): the best action in the form (dx, dy, placeBomb?),
                        the resulting coordinate from that action, and the q associated with that action
        '''
        best_q = float('-inf')
        best_a = (0, 0)
        best_n = (-1, -1)
        a_q = []

        # loop through all possible character actions in the given state
        neighbors = Util.get_neighbors(self.x, self.y, wrld)
        for n in neighbors:
            if Util_Q.explosion_distance_q(self, n, wrld) == 0:
                a = (n[0] - self.x, n[1] - self.y)
                q = self.q(n, wrld)
                if (q > best_q):
                    best_q = q
                    best_a = a
                    best_n = n
                a_q.append((a, q))

        walls = Util.walls(wrld)
        if (best_n[0], best_n[1]) in walls and not self.waiting_for_expl:
            self.place_bomb()
            self.waiting_for_expl = True

        if Util.exit_distance(best_n[0], best_n[1], wrld) >= Util.exit_distance(self.x, self.y, wrld) and not self.waiting_for_expl:
            self.place_bomb()
            self.waiting_for_expl = True

        print(a_q)
        return best_a, best_n, best_q

    def q(self, next, wrld):
        '''
        Returns the q value associated with the resulting character coordinate and world

                Parameters:
                        next (tuple): the (x, y) coordinate of where the action takes the character
                        wrld (world): The world

                Returns:
                        sum (number): the sum Q, which is the dot product of the weight and function value vectors
        '''
        sum = 0
        for i in range(len(self.weights)):
            sum += float(self.weights[i]) * self.functions[i](self, next, wrld)
        return sum

    def do(self, wrld):
        exit = Util.exit_loc(wrld)
        dist = 1 + len(Util.a_star(self.x, self.y, exit[0], exit[1], wrld, False))


        monster = Util.closest_monster(self.x, self.y, wrld)
        if monster is not None:
            monster_dist = 1 + len(Util.a_star(monster.x, monster.y, exit[0], exit[1], wrld, False))


            print("Char dist: " + str(dist))
            print("Mon dist: " + str(monster_dist))

            # win path if possible
            # if dist <= monster_dist:
            #     win_path = Util.a_star(self.x, self.y, exit[0], exit[1], wrld)
            #     past_x = self.x
            #     past_y = self.y
            #     print("win path: " + str(win_path))
            #     for move in win_path:
            #         self.move(move[0]-past_x, move[1]-past_y)
            #         past_x = self.x
            #         past_y = self.y

        # calculates Q(s,a)
        cloned_world_q = SensedWorld.from_world(wrld)

        best_move, best_next, q_s_a = self.best(cloned_world_q)

        # execute a on s, making s_prime equal to s'
        s_prime = Util_Q.next_world_q(self, best_move, wrld)[0]

        if s_prime.me(self) is None:
            q_s_a_prime = 0

        # calculates Q(s',a')
        else:
            q_s_a_prime = self.best(s_prime)[2]

        # calculates delta
        delta = Util_Q.reward(self, best_move, wrld) + GAMMA*q_s_a_prime - q_s_a

        # updates weights
        for i in range(len(self.weights)):
            self.weights[i] = float(self.weights[i]) + ALPHA*delta*self.functions[i](self, best_next, wrld)

        # write weights to file
        with open(str(self.weights_file_name) + ".txt", 'w') as savedWeights:
            writeWeights = [str(w) for w in self.weights]
            savedWeights.writelines('\n'.join(writeWeights))

        # epsilon greedy exploration
        if random.random() < self.epsilon:
            available_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
            best_move = available_moves[random.randrange(0,9)]

        print("Best Move: " + str(best_move) + " with q-value: " + str(q_s_a))

        potentially_exploded_world = SensedWorld.from_world(wrld)
        new_bomb_world, bomb_events = potentially_exploded_world.next()

        if len(new_bomb_world.bombs) == 0 and len(new_bomb_world.explosions) > 0:
            self.waiting_for_expl = False

        self.move(best_move[0], best_move[1])