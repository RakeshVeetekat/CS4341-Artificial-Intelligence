import sys
import math
from queue import PriorityQueue

sys.path.insert(0, '../bomberman')
from events import Event
from sensed_world import SensedWorld

import random

class Util:

    @classmethod
    def exit_loc(self, wrld):
        '''
        Returns the (x, y) location of the world exit

                Parameters:
                        wrld (world): The world

                Returns:
                        coords (x, y): The x and y locations of the exit, or (-1, -1) if an exit is not found
        '''
        for i in range(0, wrld.height()):
            for j in range(0, wrld.width()):
                if wrld.exit_at(j, i):
                    return (j, i)
        return (-1, -1)

    @classmethod
    def walls(self, wrld):
        '''
        Returns a list of (x, y) walls in the world

                Parameters:
                        wrld (world): The world

                Returns:
                        arr (list((x, y)): A list of all the wall coordinates in the world
        '''
        arr = [];
        for i in range(0, wrld.height()):
            for j in range(0, wrld.width()):
                if wrld.wall_at(j, i):
                    arr.append((j, i))
        return arr

    @classmethod
    def bombs(self, wrld):
        arr = [];
        for i in range(0, wrld.height()):
            for j in range(0, wrld.width()):
                if wrld.bomb_at(j, i) is not None:
                    arr.append(wrld.bomb_at(j, i))
        return arr

    @classmethod
    def explosion_next(self, x, y, wrld):
        '''
        Returns true if there is an explosion next turn at the given coords

                Parameters:
                        x (number): X coordinate to check
                        y (number): Y coordinate to check
                        wrld (world): The world

                Returns:
                        explosion (boolean): True if there is an explosion next turn, false otherwise
        '''
        return wrld.explosion_at(x, y) is not None

    @classmethod
    def exit_distance(self, x, y, wrld, measure="euclidean"):
        '''
        Returns the distance from the current position to the exit (Euclidean distance formula)

                Parameters:
                        x (number): Current x coordinate
                        y (number): Current y coordinate
                        wrld (world): Current world
                        measure (string): Defaults to Euclidean distance, but can be modified to Manhattan distance
                Returns:
                        distance (number): The distance to the exit
        '''
        (exitX, exitY) = self.exit_loc(wrld)
        if measure == "manhattan":
            return self.manhattan_distance(x, y, exitX, exitY)
        else:
            return self.euclidean_distance(x, y, exitX, exitY)

    @classmethod
    def euclidean_distance(self, fromX, fromY, toX, toY):
        '''
        Calculates the Euclidean distance between two points

                Parameters:
                        fromX (number): Start X coordinate
                        fromY (number): Start Y coordinate
                        toX (number): End X coordinate
                        toY (number): End Y coordinate

                Returns:
                        distance (number): The Euclidean distance between from and to
        '''
        return math.sqrt(math.pow(fromX - toX, 2) + math.pow(fromY - toY, 2))

    @classmethod
    def manhattan_distance(self, fromX, fromY, toX, toY):
        '''
        Calculates the Manhattan distance between two points

                Parameters:
                        fromX (number): Start X coordinate
                        fromY (number): Start Y coordinate
                        toX (number): End X coordinate
                        toY (number): End Y coordinate

                Returns:
                        distance (number): The Manhattan distance between from and to
        '''
        return math.fabs(fromX - toX) + math.fabs(fromY - toY)

    @classmethod
    def a_star(self, initialX, initialY, endX, endY, wrld, cost=True):
        '''
        Uses A* to find the path from (initialX, initialY) to (endX, endY)

                Parameters:
                        initialX (number): Start X coordinate
                        initialY (number): Start Y coordinate
                        endX (number): End X coordinate
                        endY (number): End Y coordinate
                        wrld (world): The world
                        cost (boolean): True to calculate cost, false for just the shortest path

                Returns:
                        path (list((x, y)): A list of (x, y) coordinates from start to finish according to the A* algorithm
        '''
        frontier = PriorityQueue()
        frontier.put((initialX, initialY), 0)
        came_from = {}
        cost_so_far = {}
        came_from[(initialX, initialY)] = None
        cost_so_far[(initialX, initialY)] = 0

        while not frontier.empty():
            current = frontier.get()
            if current == (endX, endY):
                path = []
                while current != (initialX, initialY):
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for next in self.get_neighbors(current[0], current[1], wrld):
                new_cost = 0
                if (cost):
                    new_cost = cost_so_far[current] + self.cost(next, wrld)
                else:
                    new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.euclidean_distance(next[0], next[1], endX, endY)
                    frontier.put(next, priority)
                    came_from[next] = current
        return []

    @classmethod
    def cost(self, next, wrld):
        '''
        Finds cost of the next move depending on certain conditions (walls, monsters, etc)

                Parameters:
                        next (x, y): The coordinate to check the cost for
                        wrld (world): The world

                Returns:
                        cost (number): The cost of this square
        '''
        next_world = SensedWorld.from_world(wrld).next()
        if wrld.wall_at(next[0], next[1]):
            return 100
        elif (next_world[0].explosion_at(next[0], next[1]) or wrld.explosion_at(next[0], next[1])) or wrld.monsters_at(next[0], next[1]) or wrld.bomb_at(next[0], next[1]):
            return 999999
        else:
            half_width = wrld.width() / 2
            if next[0] == 0 or next[0] == wrld.width():
                return 3
            elif next[0] <= half_width - (half_width / 2) or next[0] >= half_width + (half_width / 2):
                return 2
            else:
                return 1

    @classmethod
    def get_valid_moves(self, x, y, wrld):
        neighbors = self.get_neighbors(x, y, wrld)
        for x,y in neighbors:
            if wrld.wall_at(x, y):
                neighbors.remove((x,y))
        return neighbors

    @classmethod
    def get_neighbors(self, x, y, wrld):
        '''
        Finds all valid squares around the current coordinates

                Parameters:
                        x (number): The X coordinate
                        y (number): The Y coordinate
                        wrld (world): The world

                Returns:
                        neighbors (list(x, y)): The list of neighbors around (x, y)
        '''
        neighbors = []
        for dx in [-1, 0, 1]:
            if x + dx >= 0 and x + dx < wrld.width():
                for dy in [-1, 0, 1]:
                    #if (dx != 0 or dy != 0):
                        if y + dy >= 0 and y + dy < wrld.height():
                            neighbors.append((x + dx, y + dy))
        return neighbors

    @classmethod
    def get_neighbors2(self, x, y, wrld):
        '''
        Finds all valid squares that are 2 squares away from the current coordinates

                Parameters:
                        x (number): The X coordinate
                        y (number): The Y coordinate
                        wrld (world): The world

                Returns:
                        neighbors (list((x, y))): The list of neighbors 2 squares away from (x, y)
        '''
        neighbors = [];
        for dx in [-2, -1, 0, 1, 2]:
            if x + dx >= 0 and x + dx < wrld.width():
                for dy in [-2, -1, 0, 1, 2]:
                    if y + dy >= 0 and y + dy < wrld.height():
                        if (dx != 0 or dy != 0) and (dx != 1 or dy != 1):
                            neighbors.append((x + dx, y + dy))
        return neighbors

    @classmethod
    def anyMonsters(self, wrld):
        '''
        Returns true if there are any monsters in the world, false otherwise

                Parameters:
                        wrld (world): The world

                Returns:
                        True if the world has monsters, false otherwise
        '''
        if wrld.monsters == None:
            return False
        else:
            return True

    @classmethod
    def getExplosionTiles(self, wrld):
        '''
        Gets all the cells that are explosion tiles

                Parameters:
                        wrld (world): The world

                Returns:
                        explCells (list((x, y)): All the cells that will become explosion tiles
        '''
        explCells = [];
        for i in range(0, wrld.height()):
            for j in range(0, wrld.width()):
                if wrld.explosion_at(j, i):
                    explCells.append((j, i))
        return explCells

    @classmethod
    def closest_monster(self, x, y, wrld):
        '''
        Gets the closest monster to the specified coordinates

                Parameters:
                        x (number): The x coordinate
                        y (number): The y coordinate
                        wrld (world): The world

                Returns:
                    closest (MonsterEntity): The closest monster object to the player
        '''
        monsters = []
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                if wrld.monsters_at(i, j) is not None:
                    monsters.append((i, j))
        if len(monsters) == 0:
            return None
        closest = monsters[0]
        for m in monsters:
            if self.manhattan_distance(x, y, m[0], m[1]) < self.manhattan_distance(x, y, closest[0], closest[1]):
                closest = m
        closestMonster = wrld.monsters_at(closest[0], closest[1])
        return closestMonster[0]

    @classmethod
    def closest_monster_to_character(self, wrld):
        '''
        Gets the closest monster to the player

                Parameters:
                        wrld (world): The world

                Returns:
                    closest (MonsterEntity): The closest monster object to the player
        '''
        monsters = []
        for i in range(wrld.width()):
            for j in range(wrld.height()):
                if (wrld.monsters_at(i, j)):
                    monsters.append((i, j))
        if len(monsters) == 0:
            return None
        closest = monsters[0]
        c = next(iter(wrld.characters.values()))
        c = c[0]
        for m in monsters:
            if self.manhattan_distance(c.x, c.y, m[0], m[1]) < self.manhattan_distance(c.x, c.y, closest[0], closest[1]):
                closest = m
        return closest

    @classmethod
    def next_move_random(self, monsterX, monsterY, wrld):
        '''
        Gets the possible next moves for the random monster

                Parameters:
                        wrld (world): The world

                Returns:
                        cells (list((dx, dy)): The list of (x, y) directions a monster can go
        '''
        cells = []
        for dx in [-1, 0, 1]:
            if (monsterX + dx >= 0) and (monsterX + dx < wrld.width()):
                for dy in [-1, 0, 1]:
                    if (monsterY + dy >= 0) and (monsterY + dy < wrld.height()):
                        if not wrld.wall_at(monsterX + dx, monsterY + dy):
                            cells.append((dx, dy))
        return cells

    @classmethod
    def next_move_aggro(self, monster, wrld):
        '''
        Gets the possible next moves for the aggressive (self preserving) monster

                Parameters:
                        monster (MonsterEntity): The monster
                        wrld (world): The world

                Returns:
                        safe (list((dx, dy)): The list of (x, y) directions the monster can go
        '''
        if monster.name == "aggressive":
            rnge = 2
        else:
            rnge = 1

        (found, action_x, action_y) = (False, 0, 0)
        for dx in range(-rnge, rnge+1):
            # Avoid out-of-bounds access
            if ((monster.x + dx >= 0) and (monster.x + dx < wrld.width())):
                for dy in range(-rnge, rnge+1):
                    # Avoid out-of-bounds access
                    if ((monster.y + dy >= 0) and (monster.y + dy < wrld.height())):
                        # Is a character at this position?
                        if (wrld.characters_at(monster.x + dx, monster.y + dy)):
                            (found, action_x, action_y) = (True, dx, dy)
        # Get next desired position
        (nx, ny) = monster.nextpos()
        # If next pos is out of bounds, must change direction
        if (nx < 0) or (nx >= wrld.width()) or (ny < 0) or (ny >= wrld.height()):
            change_direction = True
        else:
            # If these cells are an explosion, a wall, or a monster, go away
            change_direction = (wrld.explosion_at(monster.x, monster.y) or
                                     wrld.wall_at(nx, ny) or
                                     wrld.monsters_at(nx, ny) or
                                     wrld.exit_at(nx, ny))
        if found and not change_direction:
            return action_x, action_y

        if (monster.dx == 0 and monster.dy == 0) or change_direction:
            # List of empty cells
            safe = []
            # Go through neighboring cells
            for dx in [-1, 0, 1]:
                # Avoid out-of-bounds access
                if ((monster.x + dx >= 0) and (monster.x + dx < wrld.width())):
                    for dy in [-1, 0, 1]:
                        # Avoid out-of-bounds access
                        if ((monster.y + dy >= 0) and (monster.y + dy < wrld.height())):
                            # Is this cell safe?
                            if (wrld.exit_at(monster.x + dx, monster.y + dy) or
                                    wrld.empty_at(monster.x + dx, monster.y + dy)):
                                # Yes
                                safe.append((dx, dy))
            if not safe:
                return (0, 0)
            return random.choice(safe)
        else:
            return monster.dx, monster.dy


    @classmethod
    def generateCostGraph(self, wrld):
        if self.anyMonsters(wrld):
            # Expectimax

            return 0
        else:
            costGraph = [[0] * wrld.width()] * wrld.height()
            for i in range(0, wrld.height()):
                for j in range(0, wrld.width()):
                    # Assign different costs based on free spaces, walls, bombs, and explosions
                    if self.empty_at(wrld, j, i):
                        costGraph[i][j] = 1
                    if self.wall_at(wrld, j, i):
                        costGraph[i][j] = 1000000000
                    if self.explosion_at(wrld, j, i):
                        costGraph[i][j] = 1000000000
                    if self.bomb_at(wrld, j, i) and wrld.bomb_time == 1:
                        # If bomb is about to explode, set all relevant cells with high costs
                        explCells = self.getExplosionCells(wrld, j, i)
                        for cell in explCells:
                            costGraph[cell[1]][cell[0]] = 1000000000
            return costGraph

    @classmethod
    def expectimax_search(self, wrld, depth, char):
        print("expectimax wrld")
        wrld.printit()
        c = wrld.me(char)
        if c is None:
        # accept death
            return (0, 0)
        best_action = (-1, -1)
        best_score = float("-inf")
        action_scores = []
        closest_monster = Util.closest_monster(c.x, c.y, wrld)
        print(closest_monster.name)

        # Go through the possible 8-moves of the character
        # Loop through delta x
        for dx in [-1, 0, 1]:
            # Avoid out-of-bound indexing
            if (c.x + dx >= 0) and (c.x + dx < wrld.width()):
                # Loop through delta y
                for dy in [-1, 0, 1]:
                    if (dx != 0) or (dy != 0):
                        # Avoid out-of-bound indexing
                        if (c.y + dy >= 0) and (c.y + dy < wrld.height()):
                            # No need to check impossible moves
                            if not wrld.wall_at(c.x + dx, c.y + dy):
                                # Set move in wrld

                                # if the monster is aggresive and this move brings it to within its detection range, dont do the move
                                if closest_monster.name == "aggressive" and \
                                        self.euclidean_distance(c.x+dx, c.y+dy, closest_monster.x, closest_monster.y) < 3:
                                    print("illegal move: " + str(dx) + "," + str(dy))
                                    continue
                                if (closest_monster.name == "selfpreserving" or closest_monster.name == "stupid") and \
                                        self.euclidean_distance(c.x+dx, c.y+dy, closest_monster.x, closest_monster.y) < 2:
                                    print("illegal move: " + str(dx) + "," + str(dy))
                                    continue
                                closest_monster.move(0, 0)
                                c.move(dx, dy)
                                # Get new world
                                (newwrld, events) = wrld.next()

                                action_score = self.exp_value(newwrld, events, depth, char)

                                action_scores.append(((dx,dy), action_score))

                                if action_score > best_score:
                                    best_action = (dx, dy)
                                    best_score = action_score
        print("Action scores")
        print(action_scores)
        return best_action

    @classmethod
    def exp_value(self, wrld, events, depth, char):

        if wrld.me(char) is not None:
            c = wrld.me(char)
        else:
            return -1000

        closest_monster = self.closest_monster(c.x, c.y, wrld)
        if closest_monster is None:
            return 1000

        # terminal test
        if Event.BOMB_HIT_CHARACTER in events or Event.CHARACTER_KILLED_BY_MONSTER in events:
            return -1000
        elif Event.BOMB_HIT_MONSTER in events:
            return 1000
        elif depth == 0:
            exit = self.exit_loc(wrld)
            dist_from_exit_util = 0
            dist_from_monster_util = 0

            dist_from_monster = len(self.a_star(c.x, c.y, closest_monster.x, closest_monster.y, wrld, cost=False))
            curr_dist_to_exit = len(self.a_star(c.x, c.y, exit[0], exit[1], wrld, cost=False))
            init_dist_to_exit = len(self.a_star(char.x, char.y, exit[0], exit[1], wrld, cost=False))
            spaces_closer_to_exit = init_dist_to_exit - curr_dist_to_exit

            # extra reward if the character is more than 3 spaces away
            if dist_from_monster > 4:
                dist_from_monster_util += 100
                if spaces_closer_to_exit > 3:
                    dist_from_exit_util += 100
                elif spaces_closer_to_exit > 2:
                    dist_from_exit_util += 25
                elif spaces_closer_to_exit > 0:
                    dist_from_exit_util += 10
            elif dist_from_monster > 3:
                dist_from_monster_util += 50
                if spaces_closer_to_exit > 3:
                    dist_from_exit_util += 50
                elif spaces_closer_to_exit > 2:
                    dist_from_exit_util += 10
                elif spaces_closer_to_exit > 0:
                    dist_from_exit_util += 5
            elif dist_from_monster < 3:
                dist_from_monster_util -= 1000

            # extra reward if the character is more than 2 spaces away
            if spaces_closer_to_exit > 0:
                dist_from_exit_util += 10

            return dist_from_monster_util + dist_from_exit_util

        v = 0

        if closest_monster.name == "stupid":
            possible_monster_actions = self.next_move_random(closest_monster.x, closest_monster.y, wrld)
        else:
            possible_monster_actions = self.next_move_aggro(closest_monster, wrld)
        # gross but idc
        if type(possible_monster_actions) is tuple:
            possible_monster_actions = [possible_monster_actions]

        # iterate through all possible monster moves
        for monster_action in possible_monster_actions:
            # assuming random choice for now
            p = 1/len(possible_monster_actions)

            # it seems like the aggro function returns a 2-space move, when the monster can only move 1 space, this code accounts for that
            if monster_action[0] > 0:
                monster_action = (1, monster_action[1])
            elif monster_action[0] < 0:
                monster_action = (-1, monster_action[1])

            if monster_action[1] > 0:
                monster_action = (monster_action[0], 1)
            elif monster_action[1] < 0:
                monster_action = (monster_action[0], -1)

            # move the monster
            closest_monster.move(monster_action[0], monster_action[1])
            c.move(0, 0)
            (newwrld, events) = wrld.next()

            # mutual recursion call
            v += p*self.max_value(newwrld, events, depth-1, char)

        return v

    @classmethod
    def max_value(self, wrld, events, depth, char):
        if wrld.me(char) is not None:
            c = wrld.me(char)
        else:
            return -1000

        closest_monster = self.closest_monster(c.x, c.y, wrld)
        if closest_monster is None:
            return 1000

        # terminal test
        if  (Event.BOMB_HIT_CHARACTER or Event.CHARACTER_KILLED_BY_MONSTER) in events:
            return -1000
        elif Event.BOMB_HIT_MONSTER in events:
            return 1000
        elif depth == 0:
            exit = self.exit_loc(wrld)
            dist_from_exit_util = 0
            dist_from_monster_util = 0

            dist_from_monster = len(self.a_star(c.x, c.y, closest_monster.x, closest_monster.y, wrld, cost=False))
            curr_dist_to_exit = len(self.a_star(c.x, c.y, exit[0], exit[1], wrld, cost=False))
            init_dist_to_exit = len(self.a_star(char.x, char.y, exit[0], exit[1], wrld, cost=False))
            spaces_closer_to_exit = init_dist_to_exit - curr_dist_to_exit

            # extra reward if the character is more than 2 spaces away
            if dist_from_monster > 4:
                dist_from_monster_util += 100
                if spaces_closer_to_exit > 3:
                    dist_from_exit_util += 100
                elif spaces_closer_to_exit > 2:
                    dist_from_exit_util += 25
                elif spaces_closer_to_exit > 0:
                    dist_from_exit_util += 10
            elif dist_from_monster > 3:
                dist_from_monster_util += 50
                if spaces_closer_to_exit > 3:
                    dist_from_exit_util += 50
                elif spaces_closer_to_exit > 2:
                    dist_from_exit_util += 10
                elif spaces_closer_to_exit > 0:
                    dist_from_exit_util += 5
            elif dist_from_monster < 3:
                dist_from_monster_util -= 1000

            # extra reward if the character is more than 2 spaces away
            if spaces_closer_to_exit > 0:
                dist_from_exit_util += 10

            return dist_from_monster_util + dist_from_exit_util

        v = float("-inf")

        # Go through the possible 8-moves of the character
        # Loop through delta x
        for dx in [-1, 0, 1]:
            # Avoid out-of-bound indexing
            if (c.x + dx >= 0) and (c.x + dx < wrld.width()):
                # Loop through delta y
                for dy in [-1, 0, 1]:
                    if (dx != 0) or (dy != 0):
                        # Avoid out-of-bound indexing
                        if (c.y + dy >= 0) and (c.y + dy < wrld.height()):
                            # No need to check impossible moves
                            if not wrld.wall_at(c.x + dx, c.y + dy):
                                # Set move in wrld
                                c.move(dx, dy)
                                closest_monster.move(0, 0)
                                # Get new world
                                (newwrld, events) = wrld.next()

                                # mutual recursion call
                                v = max(v, self.exp_value(newwrld, events, depth-1, char))
        return v

    @classmethod
    def closest_wall(self, x, y, wrld):
        '''
        Finds the closest wall to the player

                Parameters:
                        x (number): The x coordinate
                        y (number): The y coordinate
                        wrld (world): The world

                Returns:
                        wall ((x, y)): The closest wall that is below the player
        '''
        wall_locs = Util.walls(wrld)
        if len(wall_locs) == 0:
            return (-1, -1)

        dist_to_closest_wall = wrld.width()

        bottom_edge_locs = [(x, wrld.height()-1) for x in range(wrld.width())]
        wall_locs.append(bottom_edge_locs)

        closest_wall_loc = (0, 0)
        for wall_loc in wall_locs:
            if wall_loc[0] == x and wall_loc[1] >= y:
                wall_dist = wall_loc[1] - y
                if wall_dist < dist_to_closest_wall:
                    closest_wall_loc = wall_loc
                    dist_to_closest_wall = wall_dist
        return closest_wall_loc
