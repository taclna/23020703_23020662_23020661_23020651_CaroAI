import math

from core.constants import *

from core.game_logic import GameLogic

from ai.evaluate import Evaluator
from ai.move_generator import MoveGenerator


class AlphaBetaAI:

    nodes_searched = 0

    @staticmethod
    def get_best_move(board, depth):

        AlphaBetaAI.nodes_searched = 0

        # --- Threat detection: kiểm tra trước khi search đầy đủ ---

        moves = MoveGenerator.get_candidate_moves(board)

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

        # --- Alpha-beta search đầy đủ ---

        best_score = -math.inf
        best_move = None

        alpha = -math.inf
        beta = math.inf

        for row, col in moves:

            board[row][col] = PLAYER_O

            score = AlphaBetaAI.alphabeta(
                board,
                depth - 1,
                alpha,
                beta,
                False
            )

            board[row][col] = EMPTY

            if score > best_score:
                best_score = score
                best_move = (row, col)

            alpha = max(alpha, best_score)

        return best_move, best_score

    @staticmethod
    def alphabeta(board, depth, alpha, beta, maximizing):

        AlphaBetaAI.nodes_searched += 1

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

            value = -math.inf

            for row, col in moves:

                board[row][col] = PLAYER_O

                score = AlphaBetaAI.alphabeta(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )

                board[row][col] = EMPTY

                value = max(value, score)
                alpha = max(alpha, value)

                # Prune
                if beta <= alpha:
                    break

            return value

        # MIN (người chơi)
        else:

            value = math.inf

            for row, col in moves:

                board[row][col] = PLAYER_X

                score = AlphaBetaAI.alphabeta(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    True
                )

                board[row][col] = EMPTY

                value = min(value, score)
                beta = min(beta, value)

                # Prune
                if beta <= alpha:
                    break

            return value