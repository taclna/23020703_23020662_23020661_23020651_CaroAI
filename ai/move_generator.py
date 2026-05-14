from core.constants import *


class MoveGenerator:

    @staticmethod
    def get_candidate_moves(board, sort=True):
        """
        Trả về danh sách các ô trống xung quanh quân đã đặt,
        trong vùng bán kính 2. Nếu sort=True, ưu tiên ô gần
        nhiều quân hơn để alpha-beta prune hiệu quả hơn.
        """

        candidates = set()
        has_piece = False

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                if board[row][col] == EMPTY:
                    continue

                has_piece = True

                # Mở rộng bán kính tìm kiếm lên 2 (thay vì 1)
                for dr in range(-2, 3):
                    for dc in range(-2, 3):

                        if dr == 0 and dc == 0:
                            continue

                        nr, nc = row + dr, col + dc

                        if (
                            0 <= nr < BOARD_SIZE
                            and 0 <= nc < BOARD_SIZE
                            and board[nr][nc] == EMPTY
                        ):
                            candidates.add((nr, nc))

        # Nước đầu tiên → đặt giữa bàn
        if not has_piece:
            return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]

        if not sort:
            return list(candidates)

        # Sắp xếp: ưu tiên ô gần nhiều quân nhất
        # → alpha-beta sẽ prune nhiều hơn vì xét nước tốt trước
        def move_priority(pos):
            r, c = pos
            score = 0
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < BOARD_SIZE
                        and 0 <= nc < BOARD_SIZE
                        and board[nr][nc] != EMPTY
                    ):
                        score += 1
            return -score  # Âm để sort giảm dần

        return sorted(candidates, key=move_priority)