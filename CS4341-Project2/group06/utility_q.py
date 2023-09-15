import sys
import random

sys.path.insert(0, '../bomberman')

from entity import CharacterEntity
from sensed_world import SensedWorld, Event
from utility_scenario_one import Util

class Util_Q:

    @classmethod
    def exit_distance_q(self, char, next, wrld):
        '''
        Feature for distance to exit. 0=far from exit, 1=at exit
        '''
        exit = Util.exit_loc(wrld)
        dist = 1+len(Util.a_star(next[0], next[1], exit[0], exit[1], wrld, False))
        
        if dist == 0:
            return 1
        normal_dist = 1/(dist**2)

        return normal_dist

    @classmethod
    def closest_wall_below_distance_q(self, char, next, wrld):
        wall_locs = Util.walls(wrld)

        if len(wall_locs) == 0:
            return 0

        dist_to_closest_wall = wrld.width()

        # so that it considers the bottom edge a 'wall'
        bottom_edge_locs = [(x, wrld.height()-1) for x in range(wrld.width())]
        wall_locs.append(bottom_edge_locs)

        closest_wall_loc = (0, 0)
        for wall_loc in wall_locs:
            if wall_loc[0] == next[0] and wall_loc[1] >= next[1]:
                wall_dist = wall_loc[1] - next[1]
                if wall_dist < dist_to_closest_wall:
                    closest_wall_loc = wall_loc
                    dist_to_closest_wall = wall_dist

        if closest_wall_loc in bottom_edge_locs:
            return 0
        elif dist_to_closest_wall == 0:
            normal_dist = 1
        else:
            normal_dist = 1/(dist_to_closest_wall**4)

        return normal_dist

    @classmethod
    def closest_edge_distance_q(self, char, next, wrld):
        dist_to_left = next[0]+1
        dist_to_right = abs(wrld.width()-next[0])
        dist_to_top = next[1]+1
        dist_to_bottom = abs(wrld.height()-next[1])

        if (dist_to_left > dist_to_right and dist_to_top > dist_to_right) \
                and (dist_to_left > dist_to_bottom and dist_to_top > dist_to_bottom) \
                and dist_to_bottom < 4 and dist_to_right < 4:
            return 0

        dist_to_closest_edge = min(dist_to_top, dist_to_bottom, dist_to_left, dist_to_right)
        normal_dist = 1/(dist_to_closest_edge**4)

        return normal_dist

    @classmethod
    def explosion_distance_q(self, char, next, wrld):
        '''
        1=we are in the explosion radius,0=if not
        '''
        bombs = Util.bombs(wrld)
        if len(bombs) == 0:
            return 0
        bomb = bombs[0]
        cloned = SensedWorld.from_world(wrld)
        cloned.add_blast(bomb)
        if cloned.explosion_at(next[0], next[1]) is not None:
            return 1
        return 0

    @classmethod
    def monster_distance_q(self, char, next, wrld):
        monster = Util.closest_monster(next[0], next[1], wrld)
        if monster is not None:
            monster_dist = 1+len(Util.a_star(next[0], next[1], monster.x, monster.y, wrld))
            if monster_dist == 0:
                return 1
            normal_dist = 1/(monster_dist**4)
            return normal_dist
        else:
            return 0

    @classmethod
    def next_world_q(self, char, a, wrld):
        clone = SensedWorld.from_world(wrld)
        if clone.me(char) is not None:
            clone.me(char).move(a[0], a[1])

        closest_monster = Util.closest_monster(char.x + a[0], char.y + a[1], wrld)
        if closest_monster is not None:
            m = clone.monsters_at(closest_monster.x, closest_monster.y)
            m = m[0]
            monster_move = Util.next_move_aggro(m, wrld)
            m.move(monster_move[0], monster_move[1])

        return clone.next()

    @classmethod
    def update_weights(self, char, a, q, end, wrld):
        weights = list()
        next = (char.x + a[0], char.y + a[1])
        next_world, events = self.next_world_q(char, a, wrld)
        reward = next_world.scores['me'] - wrld.scores['me']
        if end == 1:
            reward += 2 * wrld.time
        elif end == 2:
            reward -= 500

    @classmethod
    def reward(self, char, a, wrld):
        next_from_clone, next_events = self.next_world_q(char, a, wrld)
        next_from_clone_char = next_from_clone.me(char)

        reward = 0
        if next_from_clone_char is not None:
            reward = -1
        print("reward events: " + str(next_events))
        if Event.CHARACTER_KILLED_BY_MONSTER in next_events or Event.BOMB_HIT_CHARACTER in next_events:
            reward -= 1000
        elif Event.CHARACTER_FOUND_EXIT in next_events:
            reward += 2*next_from_clone.time

        print("reward fn reward: " + str(reward))
        return reward