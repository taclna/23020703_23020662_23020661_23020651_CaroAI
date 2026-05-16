import pygame
import time

from core.constants import *
from core.game_logic import GameLogic
from core.history import MoveHistory

from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ui.compare_screen import CompareScreen

from ui.renderer import Renderer


class GameScreen:

    def __init__(self, screen, font, ai_mode):

        self.screen   = screen
        self.font     = font
        self.ai_mode  = ai_mode

        self.ai_enabled   = True
        self.player_piece = None
        self.ai_piece     = None
        self.order_pending = True

        self.renderer = Renderer(screen)

        self.board = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.current_player = PLAYER_X
        self.history        = MoveHistory()

        self.game_over   = False
        self.winner      = None
        self.ai_thinking = False

        self.nodes_searched = 0
        self.ai_score       = 0
        self.ai_time        = 0

        # ── Sidebar layout dựa hoàn toàn vào constants ──────────────────
        #   sidebar_x  = điểm bắt đầu sidebar (cạnh trái)
        #   sidebar_cx = tâm ngang của sidebar
        #   btn_x / btn_w = vị trí & chiều rộng nút (padding 20px mỗi bên)
        self.sidebar_x  = BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE + GAP_SIZE
        self.sidebar_cx = self.sidebar_x + SIDEBAR_WIDTH // 2
        self.btn_w      = SIDEBAR_WIDTH - 40          # padding 20px mỗi bên
        self.btn_x      = self.sidebar_x + 20

        # ── Vị trí y các thành phần (tính từ trên xuống) ────────────────
        #   60  → title
        #   95  → ai-mode label
        #   130 → turn label
        #   165 → divider
        #   185 → undo
        #   245 → redo
        #   305 → reset
        #   365 → toggle AI
        #   440 → divider stats
        #   460 → nodes
        #   495 → score
        #   530 → time
        #   600 → divider
        #   620 → home

        btn_h = 48

        self.undo_button      = pygame.Rect(self.btn_x, 185, self.btn_w, btn_h)
        self.redo_button      = pygame.Rect(self.btn_x, 245, self.btn_w, btn_h)
        self.reset_button     = pygame.Rect(self.btn_x, 305, self.btn_w, btn_h)
        self.toggle_ai_button = pygame.Rect(self.btn_x, 365, self.btn_w, btn_h)
        self.home_button      = pygame.Rect(self.btn_x, 620, self.btn_w, btn_h)

        # ── Dialog buttons (centred trên board) ─────────────────────────
        board_px  = BOARD_SIZE * CELL_SIZE
        dlg_cx    = BOARD_OFFSET_X + board_px // 2
        d_btn_w   = 180
        d_btn_h   = 50
        gap       = 20
        d_by      = BOARD_OFFSET_Y + board_px // 2 + 30

        self.go_first_btn  = pygame.Rect(dlg_cx - d_btn_w - gap // 2, d_by, d_btn_w, d_btn_h)
        self.go_second_btn = pygame.Rect(dlg_cx + gap // 2,            d_by, d_btn_w, d_btn_h)

    # ──────────────────────────────────────────────────────────────────────

    def _set_order(self, go_first: bool):
        if go_first:
            self.player_piece = PLAYER_X
            self.ai_piece     = PLAYER_O
        else:
            self.player_piece = PLAYER_O
            self.ai_piece     = PLAYER_X

        self.order_pending = False

        if not go_first and self.ai_enabled:
            self.ai_move()

    def reset_game(self):
        self.board          = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current_player = PLAYER_X
        self.history        = MoveHistory()
        self.game_over      = False
        self.winner         = None
        self.ai_thinking    = False
        self.nodes_searched = 0
        self.ai_score       = 0
        self.ai_time        = 0
        self.ai_enabled     = True
        self.order_pending  = True
        self.player_piece   = None
        self.ai_piece       = None

    def _toggle_ai(self):
        self.ai_enabled = not self.ai_enabled
        if self.ai_enabled:
            if self.player_piece is None:
                self.order_pending = True
            elif self.current_player == self.ai_piece:
                self.ai_move()

    # ──────────────────────────────────────────────────────────────────────
    #  DRAW
    # ──────────────────────────────────────────────────────────────────────

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        self.renderer.draw_background()
        self.renderer.draw_board()
        self.renderer.draw_sidebar()
        self.renderer.draw_pieces(self.board)

        self._draw_sidebar(mouse_pos)

        if self.order_pending and not self.game_over:
            self._draw_order_dialog(mouse_pos)

        if self.ai_thinking:
            self._draw_board_overlay("AI THINKING...")

        if self.game_over:
            if self.winner:
                if self.ai_enabled and self.player_piece:
                    msg = "You Win!" if self.winner == self.player_piece else "AI Wins!"
                else:
                    msg = f"{self.winner} Wins!"
            else:
                msg = "Draw!"
            self._draw_board_overlay(msg, sub="Reset or Home")

    # ──────────────────────────────────────────────────────────────────────
    #  SIDEBAR
    # ──────────────────────────────────────────────────────────────────────

    def _draw_sidebar(self, mouse_pos):
        cx = self.sidebar_cx

        # ── Title ────────────────────────────────────────────────────────
        title = self.font.render("CARO AI", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(cx, 48)))

        # ── AI mode ──────────────────────────────────────────────────────
        mode_name  = "Minimax" if self.ai_mode == MINIMAX else "Alpha-Beta"
        mode_surf  = self.font.render(f"AI: {mode_name}", True, TEXT_DIM)
        self.screen.blit(mode_surf, mode_surf.get_rect(center=(cx, 83)))

        # ── Divider ──────────────────────────────────────────────────────
        self._divider(cx, 107)

        # ── Turn label ───────────────────────────────────────────────────
        if self.order_pending:
            turn_label = "Choose: First / Second"
        elif self.ai_enabled:
            if self.current_player == self.player_piece:
                turn_label = f"Turn: You  ({self.current_player})"
            else:
                turn_label = f"Turn: AI  ({self.current_player})"
        else:
            turn_label = f"Turn: {self.current_player}"

        turn_surf = self.font.render(turn_label, True, TEXT_COLOR)
        self.screen.blit(turn_surf, turn_surf.get_rect(center=(cx, 145)))

        # ── Divider ──────────────────────────────────────────────────────
        self._divider(cx, 168)

        # ── Action buttons ───────────────────────────────────────────────
        self.renderer.draw_button(self.undo_button,  "Undo",  self.font, mouse_pos)
        self.renderer.draw_button(self.redo_button,  "Redo",  self.font, mouse_pos)
        self.renderer.draw_button(self.reset_button, "Reset", self.font, mouse_pos)

        # Toggle AI — coloured
        toggle_color = BTN_AI_ON if self.ai_enabled else BTN_AI_OFF
        toggle_label = "AI: ON" if self.ai_enabled else "AI: OFF"
        pygame.draw.rect(self.screen, toggle_color, self.toggle_ai_button, border_radius=10)
        toggle_surf = self.font.render(toggle_label, True, TEXT_COLOR)
        self.screen.blit(toggle_surf, toggle_surf.get_rect(center=self.toggle_ai_button.center))

        # ── Divider stats ─────────────────────────────────────────────────
        self._divider(cx, 430)

        # ── Stats ────────────────────────────────────────────────────────
        for i, (key, val) in enumerate([
            ("Nodes", str(self.nodes_searched)),
            ("Score", str(self.ai_score)),
            ("Time",  f"{self.ai_time} s"),
        ]):
            y = 455 + i * 36
            k_surf = self.font.render(f"{key}:", True, TEXT_DIM)
            v_surf = self.font.render(val,       True, TEXT_COLOR)
            self.screen.blit(k_surf, k_surf.get_rect(midright=(cx - 4, y)))
            self.screen.blit(v_surf, v_surf.get_rect(midleft=(cx + 4,  y)))

        # ── Divider home ──────────────────────────────────────────────────
        self._divider(cx, 608)

        # ── Home button ───────────────────────────────────────────────────
        self.renderer.draw_button(self.home_button, "Home", self.font, mouse_pos)

    def _divider(self, cx, y):
        half = self.btn_w // 2
        pygame.draw.line(self.screen, GRID_COLOR,
                         (cx - half, y), (cx + half, y), 1)

    # ──────────────────────────────────────────────────────────────────────
    #  ORDER DIALOG
    # ──────────────────────────────────────────────────────────────────────

    def _draw_order_dialog(self, mouse_pos):
        board_px = BOARD_SIZE * CELL_SIZE

        overlay = pygame.Surface((board_px, board_px))
        overlay.set_alpha(180)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

        dlg_w, dlg_h = 460, 190
        dlg_cx = BOARD_OFFSET_X + board_px // 2
        dlg_cy = BOARD_OFFSET_Y + board_px // 2
        dlg    = pygame.Rect(dlg_cx - dlg_w // 2, dlg_cy - dlg_h // 2, dlg_w, dlg_h)

        pygame.draw.rect(self.screen, DIALOG_BG,     dlg, border_radius=16)
        pygame.draw.rect(self.screen, DIALOG_BORDER, dlg, width=2, border_radius=16)

        title = self.font.render("Do you want to go first or second?", True, TEXT_DIALOG)
        self.screen.blit(title, title.get_rect(center=(dlg.centerx, dlg.y + 44)))

        sub = self.font.render("First = X (moves first)  |  Second = O", True, TEXT_DIALOG_SUB)
        self.screen.blit(sub, sub.get_rect(center=(dlg.centerx, dlg.y + 78)))

        # Căn nút theo dialog
        btn_w, btn_h = 178, 48
        gap          = 20
        bx = dlg.centerx - btn_w - gap // 2
        by = dlg.y + dlg_h - btn_h - 22

        self.go_first_btn  = pygame.Rect(bx,              by, btn_w, btn_h)
        self.go_second_btn = pygame.Rect(bx + btn_w + gap, by, btn_w, btn_h)

        # Go First
        c1 = BTN_FIRST_HOVER if self.go_first_btn.collidepoint(mouse_pos) else BTN_FIRST_BG
        pygame.draw.rect(self.screen, c1,             self.go_first_btn, border_radius=10)
        pygame.draw.rect(self.screen, BTN_FIRST_BORDER, self.go_first_btn, width=2, border_radius=10)
        lbl1 = self.font.render("Go First (X)", True, TEXT_COLOR)
        self.screen.blit(lbl1, lbl1.get_rect(center=self.go_first_btn.center))

        # Go Second
        c2 = BTN_SECOND_HOVER if self.go_second_btn.collidepoint(mouse_pos) else BTN_SECOND_BG
        pygame.draw.rect(self.screen, c2,              self.go_second_btn, border_radius=10)
        pygame.draw.rect(self.screen, BTN_SECOND_BORDER, self.go_second_btn, width=2, border_radius=10)
        lbl2 = self.font.render("Go Second (O)", True, TEXT_COLOR)
        self.screen.blit(lbl2, lbl2.get_rect(center=self.go_second_btn.center))

    # ──────────────────────────────────────────────────────────────────────
    #  BOARD OVERLAYS
    # ──────────────────────────────────────────────────────────────────────

    def _draw_board_overlay(self, main_text, sub=None):
        board_px = BOARD_SIZE * CELL_SIZE

        overlay = pygame.Surface((board_px, board_px))
        overlay.set_alpha(140)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

        popup_w, popup_h = 320, 130
        popup_cx = BOARD_OFFSET_X + board_px // 2
        popup_cy = BOARD_OFFSET_Y + board_px // 2
        popup    = pygame.Rect(popup_cx - popup_w // 2,
                               popup_cy - popup_h // 2,
                               popup_w, popup_h)

        pygame.draw.rect(self.screen, POPUP_BG,     popup, border_radius=14)
        pygame.draw.rect(self.screen, POPUP_BORDER, popup, width=2, border_radius=14)

        main_y = popup_cy - (14 if sub else 0)
        main_surf = self.font.render(main_text, True, TEXT_ACCENT)
        self.screen.blit(main_surf, main_surf.get_rect(center=(popup_cx, main_y)))

        if sub:
            sub_surf = self.font.render(sub, True, TEXT_DIM)
            self.screen.blit(sub_surf, sub_surf.get_rect(center=(popup_cx, popup_cy + 26)))

    # ──────────────────────────────────────────────────────────────────────
    #  EVENTS
    # ──────────────────────────────────────────────────────────────────────

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if self.order_pending and self.ai_enabled:
                if self.go_first_btn.collidepoint((mouse_x, mouse_y)):
                    self._set_order(go_first=True)
                elif self.go_second_btn.collidepoint((mouse_x, mouse_y)):
                    self._set_order(go_first=False)
                return GAME_SCREEN

            if self.home_button.collidepoint((mouse_x, mouse_y)):
                return HOME_SCREEN

            if self.toggle_ai_button.collidepoint((mouse_x, mouse_y)):
                self._toggle_ai()
                return GAME_SCREEN

            if self.undo_button.collidepoint((mouse_x, mouse_y)):
                if self.ai_enabled:
                    self.history.undo(self.board)
                    player = self.history.undo(self.board)
                    if player:
                        self.current_player = self.player_piece
                        self.game_over = False
                        self.winner    = None
                else:
                    player = self.history.undo(self.board)
                    if player:
                        self.current_player = player
                        self.game_over = False
                        self.winner    = None

            elif self.redo_button.collidepoint((mouse_x, mouse_y)):
                if self.ai_enabled:
                    self.history.redo(self.board)
                    player = self.history.redo(self.board)
                    if player:
                        self.current_player = self.player_piece
                else:
                    player = self.history.redo(self.board)
                    if player:
                        self.current_player = (
                            PLAYER_O if player == PLAYER_X else PLAYER_X
                        )

            elif self.reset_button.collidepoint((mouse_x, mouse_y)):
                self.reset_game()

            elif (
                not self.game_over
                and not self.ai_thinking
                and BOARD_OFFSET_X <= mouse_x <= BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE
                and BOARD_OFFSET_Y <= mouse_y <= BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE
            ):
                if self.ai_enabled and self.current_player == self.ai_piece:
                    return GAME_SCREEN

                col = (mouse_x - BOARD_OFFSET_X) // CELL_SIZE
                row = (mouse_y - BOARD_OFFSET_Y) // CELL_SIZE

                if self.board[row][col] == EMPTY:
                    self.board[row][col] = self.current_player
                    self.history.add_move(row, col, self.current_player)

                    if GameLogic.check_win(self.board, self.current_player):
                        self.game_over = True
                        self.winner    = self.current_player

                    elif GameLogic.check_draw(self.board):
                        self.game_over = True
                        self.winner    = None

                    else:
                        self.current_player = (
                            PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
                        )
                        if self.ai_enabled and self.current_player == self.ai_piece:
                            self.ai_move()

        return GAME_SCREEN

    # ──────────────────────────────────────────────────────────────────────
    #  AI MOVE
    # ──────────────────────────────────────────────────────────────────────

    def ai_move(self):
        if self.game_over:
            return

        self.ai_thinking = True
        self.draw()
        pygame.display.flip()

        start_time = time.time()

        if self.ai_mode == MINIMAX:
            move, score = MinimaxAI.get_best_move(self.board, depth=3)
            self.nodes_searched = MinimaxAI.nodes_searched
        else:
            move, score = AlphaBetaAI.get_best_move(self.board, depth=3)
            self.nodes_searched = AlphaBetaAI.nodes_searched

        self.ai_time     = round(time.time() - start_time, 4)
        self.ai_score    = score
        self.ai_thinking = False

        if move is None:
            return

        row, col = move
        self.board[row][col] = self.ai_piece
        self.history.add_move(row, col, self.ai_piece)

        if GameLogic.check_win(self.board, self.ai_piece):
            self.game_over = True
            self.winner    = self.ai_piece

        elif GameLogic.check_draw(self.board):
            self.game_over = True
            self.winner    = None

        else:
            self.current_player = self.player_piece