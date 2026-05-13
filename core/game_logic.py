from core.constants import *


class GameLogic:

    @staticmethod
    def check_win(board, player):

        directions = [
            (1, 0),   # vertical
            (0, 1),   # horizontal
            (1, 1),   # diagonal \
            (1, -1)   # diagonal /
        ]

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board[row][col] != player:
                    continue

                for dr, dc in directions:

                    count = 0

                    for i in range(WIN_COUNT):

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

                    if count == WIN_COUNT:
                        return True

        return False

    @staticmethod
    def check_draw(board):

        for row in board:
            if EMPTY in row:
                return False

        return True