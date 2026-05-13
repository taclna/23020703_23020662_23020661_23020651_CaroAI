from core.constants import *


class Evaluator:

    SCORES = {
        4: 100000,
        3: 1000,
        2: 100,
        1: 10
    }

    @staticmethod
    def evaluate(board):

        ai_score = Evaluator.score_player(
            board,
            PLAYER_O
        )

        player_score = Evaluator.score_player(
            board,
            PLAYER_X
        )

        return ai_score - player_score

    @staticmethod
    def score_player(board, player):

        total = 0

        directions = [
            (1, 0),
            (0, 1),
            (1, 1),
            (1, -1)
        ]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board[row][col] != player:
                    continue

                for dr, dc in directions:

                    count = 1

                    for i in range(1, WIN_COUNT):

                        nr = row + dr * i
                        nc = col + dc * i

                        if (
                            0 <= nr < BOARD_SIZE
                            and
                            0 <= nc < BOARD_SIZE
                            and
                            board[nr][nc] == player
                        ):
                            count += 1
                        else:
                            break

                    total += Evaluator.SCORES.get(count, 0)

        return total