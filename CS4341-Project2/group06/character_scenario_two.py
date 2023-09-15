# This is necessary to find the main code
import sys

sys.path.insert(0, '../bomberman')
# Import necessary stuff
from sensed_world import SensedWorld
from entity import CharacterEntity
from colorama import Fore, Back
from utility import Util

class CharacterScenarioTwo(CharacterEntity):
    def __init__(self, name, avatar, x, y, expectimax_range):
        CharacterEntity.__init__(self, name, avatar, x, y)
        self.expectimax_range = expectimax_range

    def do(self, wrld):
        closest_monster = Util.closest_monster(self.x, self.y, wrld)
        exit = Util.exit_loc(wrld)
        us_exit = Util.a_star(self.x, self.y, exit[0], exit[1], wrld)

        if wrld.wall_at(us_exit[0][0], us_exit[0][1]):
            self.place_bomb()
       
        cloned_world = SensedWorld.from_world(wrld)
        next_next_world, next_next_events = cloned_world.next()[0].next()
        killed_by_bomb = False
        for event in next_next_events:
        # again gross but idc
            if event.tpe == 2:
                killed_by_bomb = True
        
        # do we die from a bomb
        if killed_by_bomb:
            # cheat death
            #print("I know i will die next move")
            self.move(1, -1)
            return

        # if the next A* move has a cost of infinity
        if Util.cost(us_exit[0], wrld) == 999999:
            self.move(0, 0)
            return

        if closest_monster is None:
            self.move(us_exit[0][0] - self.x, us_exit[0][1] - self.y)
            return

        cloned_world = SensedWorld.from_world(wrld)

        c = cloned_world.me(self)
        if c is None:
            # accept death
            self.move(0, 0)

        m = cloned_world.monsters_at(closest_monster.x, closest_monster.y)[0]
        if m.name == "stupid":
            possible_monster_actions = Util.next_move_random(m.x, m.y, wrld)
        else:
            possible_monster_actions = Util.next_move_aggro(m, wrld)
        # gross but idc
        if type(possible_monster_actions) is tuple:
            possible_monster_actions = [possible_monster_actions]

        expected_monster_action = possible_monster_actions[0]

        # it seems like the aggro function returns a 2-space move, when the monster can only move 1 space, this code accounts for that
        if expected_monster_action[0] > 0:
            expected_monster_action = (1, expected_monster_action[1])
        elif expected_monster_action[0] < 0:
            expected_monster_action = (-1, expected_monster_action[1])

        if expected_monster_action[1] > 0:
            expected_monster_action = (expected_monster_action[0], 1)
        elif expected_monster_action[1] < 0:
            expected_monster_action = (expected_monster_action[0], -1)

        # moving the monster but keeping the character in the same place
        m.move(expected_monster_action[0], expected_monster_action[1])
        c.move(0, 0)

        # next world and getting the next versions of ourselves
        next_world, next_events = cloned_world.next()
        c_next = next_world.me(c)

        if c_next is None:
            self.move(0, 0)
            return

        m_next = Util.closest_monster(c_next.x, c_next.y, next_world)

        mon_exit_path_distance = float("inf")
        # either character or monster dies next turn. either way, lets not move.
        if m_next is not None:
            monster_distance = len(Util.a_star(c_next.x, c_next.y, m_next.x, m_next.y, wrld, cost=False))
            mon_exit_path_distance = len(Util.a_star(m_next.x, m_next.y, exit[0], exit[1], wrld, cost=False))

        us_exit_path = Util.a_star(c_next.x, c_next.y, exit[0], exit[1], wrld)

        if mon_exit_path_distance > len(us_exit_path):
            # book it
            self.move(us_exit_path[0][0] - self.x, us_exit_path[0][1] - self.y)
        else:
            if monster_distance <= self.expectimax_range:
                self.place_bomb()
                best_move = Util.expectimax_search(next_world, 2, self)
                #print("expectimax choice: " + str(best_move))
                self.move(best_move[0], best_move[1])
            else:
                best_move = (us_exit_path[0][0] - self.x, us_exit_path[0][1] - self.y)
                self.move(best_move[0], best_move[1])
        # self.place_bomb()

