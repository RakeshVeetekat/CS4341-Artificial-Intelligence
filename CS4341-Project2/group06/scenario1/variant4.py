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
#from qcharacter import QCharacter
from character_scenario_one import CharacterScenarioOne

# Create the game
#random.seed(123) # TODO Change this if you want different random choices
EPSILON = 0.1
#for i in range(0, 50):
#    print("Iteration: " + str(i))
#    print("Epsilon: " + str(EPSILON))

g = Game.fromfile('map.txt')
g.add_monster(SelfPreservingMonster("aggressive", # name
                                    "A",          # avatar
                                    3, 13,        # position
                                    2             # detection range
))
g.add_character(CharacterScenarioOne("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              5  # monster distance to invoke expectimax
))


    # with open("v4_weights.txt") as w:
    #     weights = w.read().split("\n")

    # # TODO Add your character
    # g.add_character(QCharacter("me", # name
    #                               "C",  # avatar
    #                               0, 0, # position
    #                            weights, # weights
    #                            "v4_weights", # weights file name
    #                            EPSILON, # epsilon
    # ))
    # Run!
g.go(1)
