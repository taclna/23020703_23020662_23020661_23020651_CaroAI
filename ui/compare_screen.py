import pygame
import time
import threading

from copy import deepcopy

from core.constants import *
from core.game_logic import GameLogic
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI


class CompareScreen:

    # ──────────────────────────────────────────────────────────────────────
    #  LAYOUT CONSTANTS
    # ──────────────────────────────────────────────────────────────────────

    _CELL     = 36
    _BOARD_PX = BOARD_SIZE * _CELL           # 324
    _GAP      = 30
    _BOARD_Y  = 108
    _TOTAL_W  = _BOARD_PX * 2 + _GAP        # 678
    _LEFT_X   = (WINDOW_WIDTH - _TOTAL_W) // 2   # 36
    _RIGHT_X  = _LEFT_X + _BOARD_PX + _GAP       # 390
    _MID_X    = WINDOW_WIDTH // 2

    _STATS_Y  = _BOARD_Y + _BOARD_PX + 16   # 448
    # 5 nút: Undo | Redo | Reset | Toggle AI | Home
    _BTN_Y    = _STATS_Y + 3 * 30 + 8       # 546
    _BTN_H    = 44
    _BTN_W    = (_TOTAL_W - 6 * 8) // 5     # ~123
    _BTN_GAP  = (_TOTAL_W - 5 * _BTN_W) // 6

    # ──────────────────────────────────────────────────────────────────────
    #  INIT
    # ──────────────────────────────────────────────────────────────────────

    def __init__(self, screen, font):
        self.screen = screen
        self.font   = font

        self._init_state()

        # ── 5 nút căn đều ───────────────────────────────────────────────
        lx = self._LEFT_X
        for i, name in enumerate(["undo", "redo", "reset", "toggle_ai", "home"]):
            x = lx + self._BTN_GAP + i * (self._BTN_W + self._BTN_GAP)
            setattr(self, f"{name}_button",
                    pygame.Rect(x, self._BTN_Y, self._BTN_W, self._BTN_H))

    # ──────────────────────────────────────────────────────────────────────

    def _init_state(self):
        self.board_minimax   = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.board_alphabeta = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]

        self.current_player = PLAYER_X

        # Thứ tự đi
        self.order_pending = True
        self.player_piece  = None
        self.ai_piece      = None

        # Toggle AI
        self.ai_enabled = True

        self.minimax_nodes   = 0; self.minimax_time   = 0; self.minimax_score   = 0
        self.alphabeta_nodes = 0; self.alphabeta_time = 0; self.alphabeta_score = 0

        self.game_over        = False
        self.winner_minimax   = None
        self.winner_alphabeta = None

        self.minimax_thinking   = False
        self.alphabeta_thinking = False

        self.undo_stack: list = []
        self.redo_stack: list = []

    def reset_game(self):
        self._init_state()

    # ──────────────────────────────────────────────────────────────────────
    #  ORDER
    # ──────────────────────────────────────────────────────────────────────

    def _set_order(self, go_first: bool):
        if go_first:
            self.player_piece = PLAYER_X
            self.ai_piece     = PLAYER_O
        else:
            self.player_piece = PLAYER_O
            self.ai_piece     = PLAYER_X
            self.current_player = PLAYER_X   # AI (X) đi trước

        self.order_pending = False

        # Nếu người chọn đi sau → AI đi nước đầu
        if not go_first and self.ai_enabled:
            self._run_ai_parallel()

    def _toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        if self.ai_enabled:
            if self.player_piece is None:
                self.order_pending = True
            elif self.current_player == self.ai_piece:
                self._run_ai_parallel()

    # ──────────────────────────────────────────────────────────────────────
    #  DRAW
    # ──────────────────────────────────────────────────────────────────────

    def draw(self):
        mouse = pygame.mouse.get_pos()
        self.screen.fill(BG_COLOR)

        self._draw_header()
        self._draw_board(self.board_minimax,   self._LEFT_X,  self._BOARD_Y)
        self._draw_board(self.board_alphabeta, self._RIGHT_X, self._BOARD_Y)
        self._draw_thinking_overlay_if(self.minimax_thinking,   self._LEFT_X)
        self._draw_thinking_overlay_if(self.alphabeta_thinking, self._RIGHT_X)
        self._draw_winner_overlay_if(self.winner_minimax,   self._LEFT_X)
        self._draw_winner_overlay_if(self.winner_alphabeta, self._RIGHT_X)
        self._draw_stats()
        self._draw_buttons(mouse)
        self._draw_turn_bar()

        if self.order_pending and not self.game_over:
            self._draw_order_dialog(mouse)

    # ── Header ───────────────────────────────────────────────────────────

    def _draw_header(self):
        cx_l = self._LEFT_X  + self._BOARD_PX // 2
        cx_r = self._RIGHT_X + self._BOARD_PX // 2

        for cx, label in [(cx_l, "Minimax"), (cx_r, "Alpha-Beta")]:
            s = self.font.render(label, True, TEXT_COLOR)
            self.screen.blit(s, s.get_rect(center=(cx, 38)))

        pygame.draw.line(self.screen, GRID_COLOR,
                         (self._LEFT_X, 58),
                         (self._RIGHT_X + self._BOARD_PX, 58), 1)

        title = self.font.render("COMPARE", True, TEXT_DIM)
        self.screen.blit(title, title.get_rect(center=(self._MID_X, 78)))

    # ── Turn bar ──────────────────────────────────────────────────────────

    def _draw_turn_bar(self):
        if self.game_over or self.order_pending:
            return
        if self._any_thinking():
            label = "AI thinking..."
        elif not self.ai_enabled:
            label = f"Turn: Player {self.current_player}  (AI OFF)"
        elif self.current_player == self.player_piece:
            label = f"Turn: You  ({self.current_player})"
        else:
            label = f"Turn: AI  ({self.current_player})"
        s = self.font.render(label, True, TEXT_DIM)
        self.screen.blit(s, s.get_rect(center=(self._MID_X, 93)))

    # ── Board ─────────────────────────────────────────────────────────────

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
                    off = 10
                    pygame.draw.line(self.screen, X_COLOR,
                                     (cx-off, cy-off), (cx+off, cy+off), 2)
                    pygame.draw.line(self.screen, X_COLOR,
                                     (cx+off, cy-off), (cx-off, cy+off), 2)
                elif v == PLAYER_O:
                    pygame.draw.circle(self.screen, O_COLOR, (cx, cy), 11, 2)

    # ── Overlay thinking ──────────────────────────────────────────────────

    def _draw_thinking_overlay_if(self, thinking, sx):
        if not thinking:
            return
        ov = pygame.Surface((self._BOARD_PX, self._BOARD_PX))
        ov.set_alpha(150)
        ov.fill(OVERLAY_COLOR)
        self.screen.blit(ov, (sx, self._BOARD_Y))

        pw, ph = self._BOARD_PX - 60, 60
        pr = pygame.Rect(sx + 30,
                         self._BOARD_Y + self._BOARD_PX//2 - ph//2,
                         pw, ph)
        pygame.draw.rect(self.screen, POPUP_BG,     pr, border_radius=12)
        pygame.draw.rect(self.screen, POPUP_BORDER, pr, width=1, border_radius=12)
        t = self.font.render("THINKING...", True, TEXT_ACCENT)
        self.screen.blit(t, t.get_rect(center=pr.center))

    # ── Overlay winner ────────────────────────────────────────────────────

    def _draw_winner_overlay_if(self, winner, sx):
        if not winner:
            return
        # Overlay tối phủ toàn bộ bàn cờ
        ov = pygame.Surface((self._BOARD_PX, self._BOARD_PX))
        ov.set_alpha(130)
        ov.fill(OVERLAY_COLOR)
        self.screen.blit(ov, (sx, self._BOARD_Y))

        # Popup hiện phía TRÊN bàn cờ (không che bàn cờ)
        pw, ph = self._BOARD_PX - 20, 36
        pr = pygame.Rect(sx + 10, self._BOARD_Y - ph - 6, pw, ph)
        pygame.draw.rect(self.screen, POPUP_BG,     pr, border_radius=10)
        pygame.draw.rect(self.screen, POPUP_BORDER, pr, width=1, border_radius=10)

        if winner == "Draw":
            msg = "Draw!"
        elif self.player_piece and winner == self.player_piece:
            msg = "You Win!"
        else:
            msg = "AI Wins!"
        t = self.font.render(msg, True, TEXT_ACCENT)
        self.screen.blit(t, t.get_rect(center=pr.center))

    # ── Stats ─────────────────────────────────────────────────────────────

    def _draw_stats(self):
        cx_l = self._LEFT_X  + self._BOARD_PX // 2
        cx_r = self._RIGHT_X + self._BOARD_PX // 2

        for cx, nodes, score, t in [
            (cx_l, self.minimax_nodes,   self.minimax_score,   self.minimax_time),
            (cx_r, self.alphabeta_nodes, self.alphabeta_score, self.alphabeta_time),
        ]:
            for i, (k, v) in enumerate([
                ("Nodes", str(nodes)),
                ("Score", str(score)),
                ("Time",  f"{t} s"),
            ]):
                y = self._STATS_Y + i * 30 + 12
                ks = self.font.render(f"{k}:", True, TEXT_DIM)
                vs = self.font.render(v,       True, TEXT_COLOR)
                self.screen.blit(ks, ks.get_rect(midright=(cx - 4, y)))
                self.screen.blit(vs, vs.get_rect(midleft=(cx + 4,  y)))

    # ── Buttons ───────────────────────────────────────────────────────────

    def _draw_buttons(self, mouse):
        # Undo / Redo / Reset / Home — nút thường
        for rect, label in [
            (self.undo_button,  "Undo"),
            (self.redo_button,  "Redo"),
            (self.reset_button, "Reset"),
            (self.home_button,  "Home"),
        ]:
            color = BUTTON_HOVER if rect.collidepoint(mouse) else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            s = self.font.render(label, True, TEXT_COLOR)
            self.screen.blit(s, s.get_rect(center=rect.center))

        # Toggle AI — màu trạng thái
        ai_color = BTN_AI_ON if self.ai_enabled else BTN_AI_OFF
        ai_label = "AI: ON" if self.ai_enabled else "AI: OFF"
        pygame.draw.rect(self.screen, ai_color, self.toggle_ai_button, border_radius=10)
        s = self.font.render(ai_label, True, TEXT_COLOR)
        self.screen.blit(s, s.get_rect(center=self.toggle_ai_button.center))

    # ── Order dialog ──────────────────────────────────────────────────────

    def _draw_order_dialog(self, mouse):
        # Dim cả hai board
        ov = pygame.Surface((self._TOTAL_W, self._BOARD_PX))
        ov.set_alpha(180)
        ov.fill(OVERLAY_COLOR)
        self.screen.blit(ov, (self._LEFT_X, self._BOARD_Y))

        dlg_w, dlg_h = 460, 190
        dlg = pygame.Rect(self._MID_X - dlg_w//2,
                          self._BOARD_Y + self._BOARD_PX//2 - dlg_h//2,
                          dlg_w, dlg_h)
        pygame.draw.rect(self.screen, DIALOG_BG,     dlg, border_radius=16)
        pygame.draw.rect(self.screen, DIALOG_BORDER, dlg, width=2, border_radius=16)

        t = self.font.render("Do you want to go first or second?", True, TEXT_DIALOG)
        self.screen.blit(t, t.get_rect(center=(dlg.centerx, dlg.y + 44)))

        sub = self.font.render("First = X (moves first)  |  Second = O", True, TEXT_DIALOG_SUB)
        self.screen.blit(sub, sub.get_rect(center=(dlg.centerx, dlg.y + 78)))

        btn_w, btn_h = 178, 48
        gap = 20
        bx  = dlg.centerx - btn_w - gap // 2
        by  = dlg.y + dlg_h - btn_h - 22

        self._go_first_btn  = pygame.Rect(bx,              by, btn_w, btn_h)
        self._go_second_btn = pygame.Rect(bx + btn_w + gap, by, btn_w, btn_h)

        c1 = BTN_FIRST_HOVER if self._go_first_btn.collidepoint(mouse) else BTN_FIRST_BG
        pygame.draw.rect(self.screen, c1,               self._go_first_btn,  border_radius=10)
        pygame.draw.rect(self.screen, BTN_FIRST_BORDER, self._go_first_btn,  width=2, border_radius=10)
        l1 = self.font.render("Go First (X)", True, TEXT_COLOR)
        self.screen.blit(l1, l1.get_rect(center=self._go_first_btn.center))

        c2 = BTN_SECOND_HOVER if self._go_second_btn.collidepoint(mouse) else BTN_SECOND_BG
        pygame.draw.rect(self.screen, c2,                self._go_second_btn, border_radius=10)
        pygame.draw.rect(self.screen, BTN_SECOND_BORDER, self._go_second_btn, width=2, border_radius=10)
        l2 = self.font.render("Go Second (O)", True, TEXT_COLOR)
        self.screen.blit(l2, l2.get_rect(center=self._go_second_btn.center))

    # ──────────────────────────────────────────────────────────────────────
    #  EVENTS
    # ──────────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return COMPARE_SCREEN

        mx, my = event.pos

        # ── Order dialog ──────────────────────────────────────────────────
        if self.order_pending:
            if hasattr(self, "_go_first_btn") and self._go_first_btn.collidepoint((mx, my)):
                self._set_order(go_first=True)
            elif hasattr(self, "_go_second_btn") and self._go_second_btn.collidepoint((mx, my)):
                self._set_order(go_first=False)
            return COMPARE_SCREEN

        # ── Home ──────────────────────────────────────────────────────────
        if self.home_button.collidepoint((mx, my)):
            return HOME_SCREEN

        # ── Reset ─────────────────────────────────────────────────────────
        if self.reset_button.collidepoint((mx, my)):
            self.reset_game()
            return COMPARE_SCREEN

        # ── Toggle AI ─────────────────────────────────────────────────────
        if self.toggle_ai_button.collidepoint((mx, my)):
            self._toggle_ai()
            return COMPARE_SCREEN

        # ── Undo ──────────────────────────────────────────────────────────
        if self.undo_button.collidepoint((mx, my)):
            if self.undo_stack:
                self.redo_stack.append(self._snapshot())
                self._restore(self.undo_stack.pop())
            return COMPARE_SCREEN

        # ── Redo ──────────────────────────────────────────────────────────
        if self.redo_button.collidepoint((mx, my)):
            if self.redo_stack:
                self.undo_stack.append(self._snapshot())
                self._restore(self.redo_stack.pop())
            return COMPARE_SCREEN

        # ── Click board (người đặt quân) ──────────────────────────────────
        in_left  = (self._LEFT_X  <= mx <= self._LEFT_X  + self._BOARD_PX
                    and self._BOARD_Y <= my <= self._BOARD_Y + self._BOARD_PX)
        in_right = (self._RIGHT_X <= mx <= self._RIGHT_X + self._BOARD_PX
                    and self._BOARD_Y <= my <= self._BOARD_Y + self._BOARD_PX)

        target_board = None
        if self.ai_enabled:
            # AI bật: chỉ click board trái, lượt người mới được đi
            if in_left and self.current_player == self.player_piece:
                target_board = "both"
        else:
            # AI tắt: click board nào cũng áp dụng cả hai (đồng bộ 2 board)
            if in_left or in_right:
                target_board = "both_no_ai"

        if target_board and not self.game_over and not self._any_thinking():
            # Tính row/col từ board được click
            if target_board == "both" or (target_board == "both_no_ai" and in_left):
                col = (mx - self._LEFT_X)  // self._CELL
                row = (my - self._BOARD_Y) // self._CELL
            else:
                col = (mx - self._RIGHT_X) // self._CELL
                row = (my - self._BOARD_Y) // self._CELL

            piece = self.current_player

            if target_board == "both":
                if self.board_minimax[row][col] != EMPTY:
                    return COMPARE_SCREEN
                self.undo_stack.append(self._snapshot())
                self.redo_stack.clear()
                self.board_minimax[row][col]   = piece
                self.board_alphabeta[row][col] = piece
                if self._check_end_both(piece):
                    return COMPARE_SCREEN
                self.current_player = self.ai_piece
                self._run_ai_parallel()

            elif target_board == "both_no_ai":
                # AI OFF: đặt quân lên cả 2 board tại cùng vị trí,
                # chỉ bỏ qua nếu ô đó đã có quân trên board được click
                if self.board_minimax[row][col] != EMPTY:
                    return COMPARE_SCREEN
                self.undo_stack.append(self._snapshot())
                self.redo_stack.clear()
                self.board_minimax[row][col]   = piece
                self.board_alphabeta[row][col] = piece
                if self._check_end_both(piece):
                    return COMPARE_SCREEN
                self.current_player = (PLAYER_O if piece == PLAYER_X else PLAYER_X)

        return COMPARE_SCREEN

    # ──────────────────────────────────────────────────────────────────────
    #  AI SONG SONG
    # ──────────────────────────────────────────────────────────────────────

    def _any_thinking(self):
        return self.minimax_thinking or self.alphabeta_thinking

    def _check_end_both(self, piece):
        """Kiểm tra thắng/hoà sau nước đi của người (cả hai board như nhau)."""
        if GameLogic.check_win(self.board_minimax, piece):
            self.winner_minimax   = piece
            self.winner_alphabeta = piece
            self.game_over = True
            return True
        if GameLogic.check_draw(self.board_minimax):
            self.winner_minimax   = "Draw"
            self.winner_alphabeta = "Draw"
            self.game_over = True
            return True
        return False

    def _run_ai_parallel(self):
        self.minimax_thinking   = True
        self.alphabeta_thinking = True
        self.draw()
        pygame.display.flip()

        mm_copy = deepcopy(self.board_minimax)
        ab_copy = deepcopy(self.board_alphabeta)

        def run_minimax():
            start = time.time()
            move, score = MinimaxAI.get_best_move(mm_copy, depth=3)
            elapsed = round(time.time() - start, 4)
            self.minimax_nodes = MinimaxAI.nodes_searched
            self.minimax_score = score
            self.minimax_time  = elapsed
            if move:
                r, c = move
                self.board_minimax[r][c] = self.ai_piece
                if GameLogic.check_win(self.board_minimax, self.ai_piece):
                    self.winner_minimax = self.ai_piece
                elif GameLogic.check_draw(self.board_minimax):
                    self.winner_minimax = "Draw"
            self.minimax_thinking = False
            self.draw(); pygame.display.flip()

        def run_alphabeta():
            start = time.time()
            move, score = AlphaBetaAI.get_best_move(ab_copy, depth=3)
            elapsed = round(time.time() - start, 4)
            self.alphabeta_nodes = AlphaBetaAI.nodes_searched
            self.alphabeta_score = score
            self.alphabeta_time  = elapsed
            if move:
                r, c = move
                self.board_alphabeta[r][c] = self.ai_piece
                if GameLogic.check_win(self.board_alphabeta, self.ai_piece):
                    self.winner_alphabeta = self.ai_piece
                elif GameLogic.check_draw(self.board_alphabeta):
                    self.winner_alphabeta = "Draw"
            self.alphabeta_thinking = False
            self.draw(); pygame.display.flip()

        t1 = threading.Thread(target=run_minimax,   daemon=True)
        t2 = threading.Thread(target=run_alphabeta, daemon=True)
        t1.start(); t2.start()
        t1.join();  t2.join()

        if not self.game_over:
            if self.winner_minimax or self.winner_alphabeta:
                self.game_over = True
            else:
                self.current_player = self.player_piece

    # ──────────────────────────────────────────────────────────────────────
    #  UNDO / REDO
    # ──────────────────────────────────────────────────────────────────────

    def _snapshot(self):
        return (
            deepcopy(self.board_minimax),
            deepcopy(self.board_alphabeta),
            self.current_player,
            self.player_piece,
            self.ai_piece,
            self.winner_minimax,
            self.winner_alphabeta,
            self.game_over,
            self.minimax_nodes,   self.minimax_score,   self.minimax_time,
            self.alphabeta_nodes, self.alphabeta_score, self.alphabeta_time,
        )

    def _restore(self, snap):
        (
            self.board_minimax,
            self.board_alphabeta,
            self.current_player,
            self.player_piece,
            self.ai_piece,
            self.winner_minimax,
            self.winner_alphabeta,
            self.game_over,
            self.minimax_nodes,   self.minimax_score,   self.minimax_time,
            self.alphabeta_nodes, self.alphabeta_score, self.alphabeta_time,
        ) = snap