# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
import random
from game import Game
from monsters.stupid_monster import StupidMonster

# TODO This is your code!
sys.path.insert(1, '../group06')
from character_scenario_one import CharacterScenarioOne
#from qcharacter import QCharacter

# Create the game
#random.seed(123) # TODO Change this if you want different random choices

EPSILON = 0.1
# EPSILON = 0
for i in range(0, 50):
    print("Iteration: " + str(i))
    print("Epsilon: " + str(EPSILON))
    g = Game.fromfile('map.txt')
    g.add_monster(StupidMonster("stupid", # name
                                "S",      # avatar
                                3, 9      # position
    ))

    with open("v2_weights.txt") as w:
        weights = w.read().split("\n")

    # TODO Add your character
    #g.add_character(QCharacter("me", # name
    #                              "C",  # avatar
    #                              0, 0, # position
    #                           weights, # weights
    #                           "v2_weights", # weights file name
    #                           EPSILON, # epsilon
    #))

    g.add_character(CharacterScenarioOne("me", # name
                                  "C", # avater
                                  0, 0,  # position
                                  2  # monster distance to invoke expectimax
                                  ))

    # Run!
    g.go(1)

    # EPSILON = EPSILON ** 1.1