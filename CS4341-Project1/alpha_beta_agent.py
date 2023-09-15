import math
import random

import agent

###########################
# Alpha-Beta Search Agent #
###########################

class AlphaBetaAgent(agent.Agent):
    """Agent that uses alpha-beta search"""

    # Class constructor.
    #
    # PARAM [string] name:      the name of this player
    # PARAM [int]    max_depth: the maximum search depth
    def __init__(self, name, max_depth):
        super().__init__(name)
        # Max search depth
        self.max_depth = max_depth
        self.cols = dict()

    # Pick a column.
    #
    # PARAM [board.Board] brd: the current board state
    # RETURN [int]: the column where the token must be added
    #
    # NOTE: make sure the column is legal, or you'll lose the game.
    def go(self, brd):
        """Search for the best move (choice of column for the token)"""
        # Your code here
        temp = brd.copy()
        highscore = float('-inf')
        bestmove = -1
        for col in brd.free_cols():
            temp = brd.copy()
            temp.add_token(col)
            score = self.min_value(temp, float('-inf'), float('inf'), self.max_depth - 1)
            #print('score for col ' + str(col) + ': ' + str(score))
            if score > highscore:
                highscore = score
                bestmove = col

        if bestmove == -1:
             return random.choice(brd.free_cols())
        return bestmove

    def terminal_test(self, board, depth):
        return depth == 0 or len(board.free_cols()) == 0 or board.get_outcome() != 0

    def utility(self, board):
        playerScore = 0
        opponentScore = 0
        successors = self.get_successors(board)

        if board.get_outcome() != 0 and board.get_outcome() != self.player:
            return -1000000

        if board.get_outcome() == self.player:
            return 1000000

        for i in range(2, board.n + 1):

            player_new_threats = self.count_new_threats(successors, self.player, i)
            playerScore += player_new_threats * math.pow(10, i)

            opp_new_threats = self.count_new_threats(successors, 1 if self.player == 2 else 2, i)
            opponentScore += opp_new_threats * math.pow(10, i)

        return playerScore - opponentScore

    def count_new_threats(self, succ_boards, piece, n):
        threats = 0;
        for (board, col_index) in succ_boards:
            y = 0
            while board.board[y][col_index] != 0 and y < board.h - 1:
                y = y + 1
            threats += self.count_n(board, piece, n, col_index, y-1)
        return threats


    def count_n(self, board, piece, n, x, y):
        count = 0
        if board.board[y][x] == piece:
            count += self.is_line_at(board, x, y, 1, 0, n, piece)
            count += self.is_line_at(board, x, y, 0, 1, n, piece)
            count += self.is_line_at(board, x, y, 1, 1, n, piece)
            count += self.is_line_at(board, x, y, 1, -1, n, piece)
        return count

    def is_line_at(self, board, x, y, dx, dy, n, piece):
        if ((x + (n - 1) * dx >= board.w) or
            (y + (n - 1) * dy < 0) or (y + (n - 1) * dy >= board.h)):
            return 0
        for i in range(1, n):
            if board.board[y + i * dy][x + i * dx] != piece:
                return 0
        return 1

    def min_value(self, board, alpha, beta, depth):
        if self.terminal_test(board, depth):
            return self.utility(board)
        v = float('inf')
        for col in board.free_cols():
            temp = board.copy()
            temp.add_token(col)
            v = min(v, self.max_value(temp, alpha, beta, depth - 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def max_value(self, board, alpha, beta, depth):
        if self.terminal_test(board, depth):
            return self.utility(board)
        v = float('-inf')
        for col in board.free_cols():
            temp = board.copy()
            temp.add_token(col)
            v = max(v, self.min_value(temp, alpha, beta, depth - 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    # Get the successors of the given board.
    #
    # PARAM [board.Board] brd: the board state
    # RETURN [list of (board.Board, int)]: a list of the successor boards,
    #                                      along with the column where the last
    #                                      token was added in it
    def get_successors(self, brd):
        """Returns the reachable boards from the given board brd. The return value is a tuple (new board state, column number where last token was added)."""
        # Get possible actions
        freecols = brd.free_cols()
        # Are there legal actions left?
        if not freecols:
            return []
        # Make a list of the new boards along with the corresponding actions
        succ = []
        for col in freecols:
            # Clone the original board
            nb = brd.copy()
            # Add a token to the new board
            # (This internally changes nb.player, check the method definition!)
            player = brd.player
            nb.player = 2 if player == 1 else 1
            nb.add_token(col)
            # Add board to list of successors
            succ.append((nb,col))
        return succ
