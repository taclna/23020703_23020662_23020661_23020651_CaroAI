import pygame
import time
import csv
import os
from copy import deepcopy
from datetime import datetime

from core.constants import *
from core.game_logic import GameLogic
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI


# ──────────────────────────────────────────────────────────────────────────────
#  5 TRẠNG THÁI KIỂM THỬ CỐ ĐỊNH
#  X = PLAYER_X, O = PLAYER_O, _ = EMPTY
# ──────────────────────────────────────────────────────────────────────────────

def _b(layout: str):
    """Chuyển chuỗi layout 9x9 thành ma trận board."""
    rows = [r.strip() for r in layout.strip().split("\n")]
    board = []
    for r in rows:
        cells = r.split()
        row = []
        for c in cells:
            if c == "X":
                row.append(PLAYER_X)
            elif c == "O":
                row.append(PLAYER_O)
            else:
                row.append(EMPTY)
        board.append(row)
    return board

E = "."

TEST_CASES = [
    {
        "name": "1. Đầu ván",
        "desc": "Bàn cờ trống hoàn toàn",
        "board": _b("""
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . X . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
"""),
        "ai_piece": PLAYER_O,
    },
    {
        "name": "2. Giữa ván",
        "desc": "Cả hai bên đang phát triển",
        "board": _b("""
. . . . . . . . .
. . . . . . . . .
. . . X O . . . .
. . . O X . . . .
. . . X O X . . .
. . . . O . . . .
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
"""),
        "ai_piece": PLAYER_O,
    },
    {
        "name": "3. AI sắp thắng",
        "desc": "O có 4 liên tiếp, cần đánh thắng",
        "board": _b("""
. . . . . . . . .
. . . . . . . . .
. . . X X . . . .
. . . . . . . . .
. . O O O O . . .
. . . X . . . . .
. . . . X . . . .
. . . . . . . . .
. . . . . . . . .
"""),
        "ai_piece": PLAYER_O,
    },
    {
        "name": "4. Người sắp thắng",
        "desc": "X có 4 liên tiếp, AI phải chặn",
        "board": _b("""
. . . . . . . . .
. . . . . . . . .
. . . . . . . . .
. . X X X X . . .
. . . O . . . . .
. . . O . . . . .
. . . O . . . . .
. . . . . . . . .
. . . . . . . . .
"""),
        "ai_piece": PLAYER_O,
    },
    {
        "name": "5. Tấn công hai hướng",
        "desc": "Nhiều nhánh phức tạp, cả hai có cơ hội",
        "board": _b("""
. . . . . . . . .
. . . X . . . . .
. . X . O . . . .
. X . O . O . . .
X . O . X . O . .
. . . X . O . . .
. . . . X . . . .
. . . . . X . . .
. . . . . . . . .
"""),
        "ai_piece": PLAYER_O,
    },
]

DEPTHS = [1, 2, 3]


class ExperimentScreen:

    # ──────────────────────────────────────────────────────────────────────
    #  LAYOUT — kế thừa từ CompareScreen
    # ──────────────────────────────────────────────────────────────────────

    _CELL     = 28
    _BOARD_PX = BOARD_SIZE * _CELL          # 252
    _GAP      = 20
    _BOARD_Y  = 100
    _TOTAL_W  = _BOARD_PX * 2 + _GAP       # 524
    _LEFT_X   = (WINDOW_WIDTH - _TOTAL_W) // 2
    _RIGHT_X  = _LEFT_X + _BOARD_PX + _GAP
    _MID_X    = WINDOW_WIDTH // 2

    # Bảng kết quả bên phải (chiếm phần còn lại)
    _TABLE_X  = _RIGHT_X + _BOARD_PX + 24
    _TABLE_W  = WINDOW_WIDTH - _TABLE_X - 16

    _BTN_H    = 36
    _BTN_Y    = WINDOW_HEIGHT - _BTN_H - 14

    # ──────────────────────────────────────────────────────────────────────
    #  INIT
    # ──────────────────────────────────────────────────────────────────────

    def __init__(self, screen, font):
        self.screen = screen
        self.font   = font

        self.case_idx  = 0          # trạng thái đang xem
        self.depth_idx = 2          # độ sâu đang chọn (index vào DEPTHS)
        self.results   = []         # list of result dicts

        self.running   = False      # đang chạy thực nghiệm
        self.status_msg = "Chọn trạng thái và độ sâu, rồi nhấn  Run  hoặc  Run All"

        self._load_case()
        self._build_buttons()

    def _load_case(self):
        tc = TEST_CASES[self.case_idx]
        self.board_minimax   = deepcopy(tc["board"])
        self.board_alphabeta = deepcopy(tc["board"])
        self.ai_piece        = tc["ai_piece"]

        self.mm_nodes = self.mm_score = self.mm_time = self.mm_move = None
        self.ab_nodes = self.ab_score = self.ab_time = self.ab_move = None

    def _build_buttons(self):
        bw, bh, gap = 100, self._BTN_H, 10
        lx = self._LEFT_X
        buttons = ["◀ Prev", "Next ▶", "Run", "Run All", "Export CSV", "Home"]
        self._buttons = {}
        for i, name in enumerate(buttons):
            self._buttons[name] = pygame.Rect(
                lx + i * (bw + gap), self._BTN_Y, bw, bh)

        # Nút chọn depth
        self._depth_btns = {}
        dx = self._TABLE_X
        for i, d in enumerate(DEPTHS):
            self._depth_btns[d] = pygame.Rect(dx + i * 60, self._BTN_Y, 50, bh)

    # ──────────────────────────────────────────────────────────────────────
    #  RUN
    # ──────────────────────────────────────────────────────────────────────

    def _run_one(self, depth):
        """Chạy Minimax + AlphaBeta trên trạng thái hiện tại với depth."""
        mm_board = deepcopy(TEST_CASES[self.case_idx]["board"])
        ab_board = deepcopy(TEST_CASES[self.case_idx]["board"])

        # Minimax
        t0 = time.time()
        mm_move, mm_score = MinimaxAI.get_best_move(mm_board, depth=depth)
        mm_time  = round(time.time() - t0, 4)
        mm_nodes = MinimaxAI.nodes_searched

        # Alpha-Beta
        t0 = time.time()
        ab_move, ab_score = AlphaBetaAI.get_best_move(ab_board, depth=depth)
        ab_time  = round(time.time() - t0, 4)
        ab_nodes = AlphaBetaAI.nodes_searched

        # Tỉ lệ giảm nodes
        pruned_pct = 0
        if mm_nodes > 0:
            pruned_pct = round((1 - ab_nodes / mm_nodes) * 100, 1)

        same_move = (mm_move == ab_move)

        result = {
            "case":       TEST_CASES[self.case_idx]["name"],
            "depth":      depth,
            "mm_nodes":   mm_nodes,
            "mm_score":   mm_score,
            "mm_time":    mm_time,
            "mm_move":    mm_move,
            "ab_nodes":   ab_nodes,
            "ab_score":   ab_score,
            "ab_time":    ab_time,
            "ab_move":    ab_move,
            "pruned_pct": pruned_pct,
            "same_move":  same_move,
        }

        # Cập nhật display
        self.mm_nodes = mm_nodes; self.mm_score = mm_score
        self.mm_time  = mm_time;  self.mm_move  = mm_move
        self.ab_nodes = ab_nodes; self.ab_score = ab_score
        self.ab_time  = ab_time;  self.ab_move  = ab_move

        # Vẽ nước đi lên board display
        if mm_move:
            r, c = mm_move
            self.board_minimax[r][c] = self.ai_piece
        if ab_move:
            r, c = ab_move
            self.board_alphabeta[r][c] = self.ai_piece

        return result

    def run_current(self):
        depth = DEPTHS[self.depth_idx]
        self.status_msg = f"Đang chạy {TEST_CASES[self.case_idx]['name']} depth={depth}..."
        self.draw(); pygame.display.flip()
        result = self._run_one(depth)
        # Tránh duplicate
        self.results = [r for r in self.results
                        if not (r["case"] == result["case"] and r["depth"] == result["depth"])]
        self.results.append(result)
        self.status_msg = (f"✓ Done  |  MM nodes={result['mm_nodes']}  "
                           f"AB nodes={result['ab_nodes']}  "
                           f"Pruned={result['pruned_pct']}%  "
                           f"Same move={'Yes' if result['same_move'] else 'No'}")

    def run_all(self):
        self.results = []
        total = len(TEST_CASES) * len(DEPTHS)
        done  = 0
        for ci, tc in enumerate(TEST_CASES):
            self.case_idx = ci
            self._load_case()
            for depth in DEPTHS:
                self.depth_idx = DEPTHS.index(depth)
                self.status_msg = f"Chạy {tc['name']}  depth={depth}  ({done+1}/{total})..."
                self.draw(); pygame.display.flip()
                result = self._run_one(depth)
                self.results.append(result)
                done += 1
        self.status_msg = f"✓ Hoàn thành {total} lần chạy! Nhấn Export CSV để lưu."

    def export_csv(self):
        folder = "reports"
        os.makedirs(folder, exist_ok=True)
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, f"experiment_{ts}.csv")
        fields = ["case", "depth",
                  "mm_nodes", "mm_score", "mm_time", "mm_move",
                  "ab_nodes", "ab_score", "ab_time", "ab_move",
                  "pruned_pct", "same_move"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(self.results)
        self.status_msg = f"✓ Đã lưu: {path}"

    # ──────────────────────────────────────────────────────────────────────
    #  DRAW
    # ──────────────────────────────────────────────────────────────────────

    def draw(self):
        mouse = pygame.mouse.get_pos()
        self.screen.fill(BG_COLOR)

        self._draw_header()
        self._draw_boards()
        self._draw_stats_panel()
        self._draw_results_table()
        self._draw_buttons(mouse)
        self._draw_status()

    # ── Header ────────────────────────────────────────────────────────────

    def _draw_header(self):
        tc = TEST_CASES[self.case_idx]
        cx_l = self._LEFT_X  + self._BOARD_PX // 2
        cx_r = self._RIGHT_X + self._BOARD_PX // 2

        for cx, label in [(cx_l, "Minimax"), (cx_r, "Alpha-Beta")]:
            s = self.font.render(label, True, TEXT_COLOR)
            self.screen.blit(s, s.get_rect(center=(cx, 22)))

        # Tên trạng thái + mô tả
        name_s = self.font.render(tc["name"], True, TEXT_ACCENT)
        self.screen.blit(name_s, name_s.get_rect(center=(self._MID_X, 42)))
        desc_s = self.font.render(tc["desc"], True, TEXT_DIM)
        self.screen.blit(desc_s, desc_s.get_rect(center=(self._MID_X, 60)))

        pygame.draw.line(self.screen, GRID_COLOR,
                         (self._LEFT_X, 74),
                         (self._RIGHT_X + self._BOARD_PX, 74), 1)

    # ── Boards ────────────────────────────────────────────────────────────

    def _draw_boards(self):
        self._draw_board(self.board_minimax,   self._LEFT_X,  self._BOARD_Y)
        self._draw_board(self.board_alphabeta, self._RIGHT_X, self._BOARD_Y)

        # Đánh dấu nước đi được chọn (highlight xanh lá)
        for move, sx in [(self.mm_move, self._LEFT_X), (self.ab_move, self._RIGHT_X)]:
            if move:
                r, c = move
                cx = sx + c * self._CELL + self._CELL // 2
                cy = self._BOARD_Y + r * self._CELL + self._CELL // 2
                pygame.draw.circle(self.screen, (80, 200, 120), (cx, cy),
                                   self._CELL // 2 - 3, 3)

    def _draw_board(self, board, sx, sy):
        c = self._CELL
        n = BOARD_SIZE
        for i in range(n + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                             (sx + i*c, sy), (sx + i*c, sy + n*c), 1)
            pygame.draw.line(self.screen, GRID_COLOR,
                             (sx, sy + i*c), (sx + n*c, sy + i*c), 1)
        for row in range(n):
            for col in range(n):
                v  = board[row][col]
                cx = sx + col*c + c//2
                cy = sy + row*c + c//2
                if v == PLAYER_X:
                    off = 7
                    pygame.draw.line(self.screen, X_COLOR,
                                     (cx-off, cy-off), (cx+off, cy+off), 2)
                    pygame.draw.line(self.screen, X_COLOR,
                                     (cx+off, cy-off), (cx-off, cy+off), 2)
                elif v == PLAYER_O:
                    pygame.draw.circle(self.screen, O_COLOR, (cx, cy), 8, 2)

    # ── Stats dưới board ──────────────────────────────────────────────────

    def _draw_stats_panel(self):
        sy = self._BOARD_Y + self._BOARD_PX + 10
        depth = DEPTHS[self.depth_idx]

        cx_l = self._LEFT_X  + self._BOARD_PX // 2
        cx_r = self._RIGHT_X + self._BOARD_PX // 2

        for cx, nodes, score, t, move in [
            (cx_l, self.mm_nodes, self.mm_score, self.mm_time, self.mm_move),
            (cx_r, self.ab_nodes, self.ab_score, self.ab_time, self.ab_move),
        ]:
            if nodes is None:
                s = self.font.render("Chưa chạy", True, TEXT_DIM)
                self.screen.blit(s, s.get_rect(center=(cx, sy + 20)))
                continue
            for i, (k, v) in enumerate([
                ("Nodes", f"{nodes:,}"),
                ("Score", str(score)),
                ("Time",  f"{t} s"),
                ("Move",  str(move) if move else "—"),
            ]):
                y = sy + i * 22 + 8
                ks = self.font.render(f"{k}:", True, TEXT_DIM)
                vs = self.font.render(v,       True, TEXT_COLOR)
                self.screen.blit(ks, ks.get_rect(midright=(cx - 4, y)))
                self.screen.blit(vs, vs.get_rect(midleft=(cx + 4,  y)))

        # Depth hiện tại
        d_s = self.font.render(f"Depth: {depth}", True, TEXT_ACCENT)
        self.screen.blit(d_s, d_s.get_rect(center=(self._MID_X, sy + 8)))

        # So sánh nếu đã chạy
        if self.mm_nodes is not None and self.ab_nodes is not None:
            pct = 0
            if self.mm_nodes > 0:
                pct = round((1 - self.ab_nodes / self.mm_nodes) * 100, 1)
            same = "✓ Cùng nước đi" if self.mm_move == self.ab_move else "✗ Khác nước đi"
            c1 = (100, 220, 130) if self.mm_move == self.ab_move else (220, 100, 100)
            for row, (txt, col) in enumerate([
                (f"AB giảm {pct}% nodes", TEXT_ACCENT),
                (same, c1),
            ]):
                s = self.font.render(txt, True, col)
                self.screen.blit(s, s.get_rect(center=(self._MID_X, sy + 30 + row * 22)))

    # ── Bảng kết quả bên phải ────────────────────────────────────────────

    def _draw_results_table(self):
        tx = self._TABLE_X
        tw = self._TABLE_W
        ty = 10
        row_h = 22

        # Tiêu đề bảng
        title = self.font.render("Kết quả thực nghiệm", True, TEXT_COLOR)
        self.screen.blit(title, (tx, ty))
        ty += 24

        if not self.results:
            s = self.font.render("(Chưa có dữ liệu)", True, TEXT_DIM)
            self.screen.blit(s, (tx, ty))
            return

        # Header
        headers = ["Trạng thái", "D", "MM nodes", "AB nodes", "Pruned%", "Same"]
        col_w   = [130, 20, 74, 74, 56, 38]
        cx = tx
        for h, w in zip(headers, col_w):
            hs = self.font.render(h, True, TEXT_DIM)
            self.screen.blit(hs, (cx, ty))
            cx += w
        ty += row_h - 2
        pygame.draw.line(self.screen, GRID_COLOR, (tx, ty), (tx + sum(col_w), ty), 1)
        ty += 4

        # Rows
        for res in self.results[-16:]:   # Hiển thị tối đa 16 dòng
            vals = [
                res["case"][:16],
                str(res["depth"]),
                f"{res['mm_nodes']:,}",
                f"{res['ab_nodes']:,}",
                f"{res['pruned_pct']}%",
                "✓" if res["same_move"] else "✗",
            ]
            color = TEXT_COLOR if res["same_move"] else (220, 160, 100)
            cx = tx
            for v, w in zip(vals, col_w):
                vs = self.font.render(v, True, color)
                self.screen.blit(vs, (cx, ty))
                cx += w
            ty += row_h
            if ty > self._BTN_Y - 10:
                break

    # ── Buttons ───────────────────────────────────────────────────────────

    def _draw_buttons(self, mouse):
        colors = {
            "◀ Prev":     BUTTON_COLOR,
            "Next ▶":     BUTTON_COLOR,
            "Run":        (50, 130, 200),
            "Run All":    (50, 160, 100),
            "Export CSV": (120, 90, 180),
            "Home":       BUTTON_COLOR,
        }
        hover_colors = {
            "◀ Prev":     BUTTON_HOVER,
            "Next ▶":     BUTTON_HOVER,
            "Run":        (70, 150, 220),
            "Run All":    (70, 190, 120),
            "Export CSV": (150, 110, 210),
            "Home":       BUTTON_HOVER,
        }
        for name, rect in self._buttons.items():
            base  = colors.get(name, BUTTON_COLOR)
            hover = hover_colors.get(name, BUTTON_HOVER)
            col   = hover if rect.collidepoint(mouse) else base
            pygame.draw.rect(self.screen, col, rect, border_radius=8)
            s = self.font.render(name, True, TEXT_COLOR)
            self.screen.blit(s, s.get_rect(center=rect.center))

        # Depth selector
        depth_label = self.font.render("Depth:", True, TEXT_DIM)
        self.screen.blit(depth_label,
                         (self._TABLE_X, self._BTN_Y + self._BTN_H // 2 - 8))
        for d, rect in self._depth_btns.items():
            active = (d == DEPTHS[self.depth_idx])
            col = TEXT_ACCENT if active else BUTTON_COLOR
            pygame.draw.rect(self.screen, col, rect, border_radius=8)
            s = self.font.render(str(d), True, TEXT_COLOR)
            self.screen.blit(s, s.get_rect(center=rect.center))

    # ── Status bar ────────────────────────────────────────────────────────

    def _draw_status(self):
        s = self.font.render(self.status_msg, True, TEXT_DIM)
        self.screen.blit(s, s.get_rect(
            midleft=(self._LEFT_X, self._BTN_Y - 16)))

    # ──────────────────────────────────────────────────────────────────────
    #  EVENTS
    # ──────────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return EXPERIMENT_SCREEN

        mx, my = event.pos

        # Depth buttons
        for d, rect in self._depth_btns.items():
            if rect.collidepoint((mx, my)):
                self.depth_idx = DEPTHS.index(d)
                return EXPERIMENT_SCREEN

        # Main buttons
        for name, rect in self._buttons.items():
            if not rect.collidepoint((mx, my)):
                continue
            if name == "◀ Prev":
                self.case_idx = (self.case_idx - 1) % len(TEST_CASES)
                self._load_case()
            elif name == "Next ▶":
                self.case_idx = (self.case_idx + 1) % len(TEST_CASES)
                self._load_case()
            elif name == "Run":
                self.run_current()
            elif name == "Run All":
                self.run_all()
            elif name == "Export CSV":
                if self.results:
                    self.export_csv()
                else:
                    self.status_msg = "Chưa có kết quả! Hãy Run hoặc Run All trước."
            elif name == "Home":
                return HOME_SCREEN
            return EXPERIMENT_SCREEN

        return EXPERIMENT_SCREEN