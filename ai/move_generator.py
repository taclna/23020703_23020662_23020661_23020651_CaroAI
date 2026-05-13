from core.constants import *


class MoveGenerator:

    @staticmethod
    def get_candidate_moves(board):

        candidates = set()

        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0), (1, 1)
        ]

        has_piece = False

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board[row][col] != EMPTY:

                    has_piece = True

                    for dr, dc in directions:

                        nr = row + dr
                        nc = col + dc

                        if (
                            0 <= nr < BOARD_SIZE
                            and
                            0 <= nc < BOARD_SIZE
                            and
                            board[nr][nc] == EMPTY
                        ):
                            candidates.add((nr, nc))

        # First move → center
        if not has_piece:
            return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]

        return list(candidates)