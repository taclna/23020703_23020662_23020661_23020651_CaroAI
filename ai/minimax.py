import math

from core.constants import *

from core.game_logic import GameLogic

from ai.evaluate import Evaluator
from ai.move_generator import MoveGenerator


class MinimaxAI:

    nodes_searched = 0

    @staticmethod
    def get_best_move(board, depth):

        MinimaxAI.nodes_searched = 0

        best_score = -math.inf
        best_move = None

        moves = MoveGenerator.get_candidate_moves(board)

        for row, col in moves:

            board[row][col] = PLAYER_O

            score = MinimaxAI.minimax(
                board,
                depth - 1,
                False
            )

            board[row][col] = EMPTY

            if score > best_score:

                best_score = score
                best_move = (row, col)

        return best_move, best_score

    @staticmethod
    def minimax(board, depth, maximizing):

        MinimaxAI.nodes_searched += 1

        # Terminal states
        if GameLogic.check_win(board, PLAYER_O):
            return 1000000

        if GameLogic.check_win(board, PLAYER_X):
            return -1000000

        if GameLogic.check_draw(board):
            return 0

        if depth == 0:
            return Evaluator.evaluate(board)

        moves = MoveGenerator.get_candidate_moves(board)

        # MAX
        if maximizing:

            best = -math.inf

            for row, col in moves:

                board[row][col] = PLAYER_O

                score = MinimaxAI.minimax(
                    board,
                    depth - 1,
                    False
                )

                board[row][col] = EMPTY

                best = max(best, score)

            return best

        # MIN
        else:

            best = math.inf

            for row, col in moves:

                board[row][col] = PLAYER_X

                score = MinimaxAI.minimax(
                    board,
                    depth - 1,
                    True
                )

                board[row][col] = EMPTY

                best = min(best, score)

            return best