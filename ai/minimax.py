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

        moves = MoveGenerator.get_candidate_moves(board)

        # --- Threat detection: kiểm tra trước khi search đầy đủ ---

        # 1. Nếu AI có thể thắng ngay → đánh luôn
        for row, col in moves:
            board[row][col] = PLAYER_O
            win = GameLogic.check_win(board, PLAYER_O)
            board[row][col] = EMPTY
            if win:
                return (row, col), 1000000

        # 2. Nếu người chơi sắp thắng → buộc phải chặn
        for row, col in moves:
            board[row][col] = PLAYER_X
            win = GameLogic.check_win(board, PLAYER_X)
            board[row][col] = EMPTY
            if win:
                return (row, col), 0

        # --- Minimax search đầy đủ ---

        best_score = -math.inf
        best_move = None

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

        moves = MoveGenerator.get_candidate_moves(board, sort=True)

        # MAX (AI)
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

        # MIN (người chơi)
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