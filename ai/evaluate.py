from core.constants import *


class Evaluator:

    # (count, open_ends) -> score
    # open_ends: số đầu trống của chuỗi (0, 1, hoặc 2)
    SCORES = {
        # 4 quân → thắng (dù chặn 1 hay 2 đầu)
        (4, 1): 100000,
        (4, 2): 100000,

        # 3 quân mở 2 đầu → cực kỳ nguy hiểm (gần như thắng)
        (3, 2): 50000,
        (3, 1): 1000,

        # 2 quân
        (2, 2): 500,
        (2, 1): 100,

        # 1 quân
        (1, 2): 10,
        (1, 1): 1,
    }

    @staticmethod
    def evaluate(board):

        ai_score = Evaluator.score_player(board, PLAYER_O)
        player_score = Evaluator.score_player(board, PLAYER_X)

        return ai_score - player_score

    @staticmethod
    def score_player(board, player):

        total = 0

        directions = [
            (1, 0),   # dọc
            (0, 1),   # ngang
            (1, 1),   # chéo xuôi
            (1, -1),  # chéo ngược
        ]

        visited = set()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board[row][col] != player:
                    continue

                for dr, dc in directions:

                    # Tránh đếm trùng: chỉ xét nếu ô trước không cùng hướng
                    pr, pc = row - dr, col - dc
                    if (
                        0 <= pr < BOARD_SIZE
                        and 0 <= pc < BOARD_SIZE
                        and board[pr][pc] == player
                    ):
                        continue  # Đây không phải đầu chuỗi → bỏ qua

                    # Đếm độ dài chuỗi
                    count = 1
                    for i in range(1, WIN_COUNT + 1):
                        nr, nc = row + dr * i, col + dc * i
                        if (
                            0 <= nr < BOARD_SIZE
                            and 0 <= nc < BOARD_SIZE
                            and board[nr][nc] == player
                        ):
                            count += 1
                        else:
                            break

                    # Kiểm tra 2 đầu có trống không
                    open_ends = 0

                    # Đầu trước (trước điểm bắt đầu chuỗi)
                    pr2, pc2 = row - dr, col - dc
                    if (
                        0 <= pr2 < BOARD_SIZE
                        and 0 <= pc2 < BOARD_SIZE
                        and board[pr2][pc2] == EMPTY
                    ):
                        open_ends += 1

                    # Đầu sau (sau điểm kết thúc chuỗi)
                    er, ec = row + dr * count, col + dc * count
                    if (
                        0 <= er < BOARD_SIZE
                        and 0 <= ec < BOARD_SIZE
                        and board[er][ec] == EMPTY
                    ):
                        open_ends += 1

                    # Chuỗi bị chặn 2 đầu → vô giá trị
                    if open_ends == 0:
                        continue

                    score = Evaluator.SCORES.get((count, open_ends), 0)
                    total += score

        return total