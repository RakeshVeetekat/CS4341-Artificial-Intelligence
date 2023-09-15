import random
import game
import agent
import alpha_beta_agent as aba

# Set random seed for reproducibility
#random.seed(1)

#
# Random vs. Random
#
#g = game.Game(7, # width
#              6, # height
#              4, # tokens in a row to win
#              agent.RandomAgent("random1"),       # player 1
#              agent.RandomAgent("random2"))       # player 2

#
# Human vs. Random
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human"),    # player 1
#               agent.RandomAgent("random"))        # player 2

#
# Random vs. AlphaBeta
#

alpha_wins = 0
beta_wins = 0
num_games = 10
for i in range(num_games):
    g = game.Game(10, # width
                  8, # height
                  5, # tokens in a row to win
                  aba.AlphaBetaAgent("alpha", 4),        # player 1
                  aba.AlphaBetaAgent("beta", 4)) # player 2
    outcome = g.go()
    if outcome == 1:
        alpha_wins += 1
    elif outcome == 2:
        beta_wins += 1
    print("Game " + str(i) + " finished. Winner was " + str(outcome))


print("Alpha won " + str(alpha_wins*100.0/num_games) + "% of games. Beta won " + str(beta_wins * 100.0/num_games) + "% of games")

#
# Human vs. AlphaBeta
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human"),    # player 1
#               aba.AlphaBetaAgent("alphabeta", 4)) # player 2

#
# Human vs. Human
#
# g = game.Game(7, # width
#               6, # height
#               4, # tokens in a row to win
#               agent.InteractiveAgent("human1"),   # player 1
#               agent.InteractiveAgent("human2"))   # player 2

# Execute the game

