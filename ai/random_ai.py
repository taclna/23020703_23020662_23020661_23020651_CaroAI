import random

from core.constants import *


class RandomAI:

    @staticmethod
    def get_move(board):

        empty_cells = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board[row][col] == EMPTY:
                    empty_cells.append((row, col))

        if not empty_cells:
            return None

        return random.choice(empty_cells)