# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.selfpreserving_monster import SelfPreservingMonster

# TODO This is your code!
sys.path.insert(1, '../group06')
from character_scenario_two import CharacterScenarioTwo

# Create the game
random.seed(123) # TODO Change this if you want different random choices
g = Game.fromfile('map.txt')
g.add_monster(SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
))

# TODO Add your character
g.add_character(CharacterScenarioTwo("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              5
))

# Run!
g.go(1)
