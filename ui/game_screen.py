import pygame

from core.constants import *
from core.game_logic import GameLogic
from core.history import MoveHistory

from ai.random_ai import RandomAI
from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI
from ui.compare_screen import CompareScreen

from ui.renderer import Renderer


class GameScreen:

    def __init__(self, screen, font, ai_mode):

        self.screen = screen
        self.font = font

        self.ai_mode = ai_mode

        self.renderer = Renderer(screen)

        self.board = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.current_player = PLAYER_X

        self.history = MoveHistory()

        self.game_over = False
        self.winner = None
        self.ai_thinking = False


        self.nodes_searched = 0
        self.ai_score = 0
        self.ai_time = 0

        board_width = BOARD_SIZE * CELL_SIZE

        self.sidebar_x = (
                BOARD_OFFSET_X
                + board_width
                + 40
        )

        # Buttons
        self.home_button = pygame.Rect(self.sidebar_x, 520, 200, 50)

        self.undo_button = pygame.Rect(self.sidebar_x, 180, 200, 50)

        self.redo_button = pygame.Rect(self.sidebar_x, 260, 200, 50)

        self.reset_button = pygame.Rect(self.sidebar_x, 340, 200, 50)

    def reset_game(self):

        self.board = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.current_player = PLAYER_X

        self.history = MoveHistory()

        self.game_over = False
        self.winner = None
        self.ai_thinking = False

        self.nodes_searched = 0
        self.ai_score = 0
        self.ai_time = 0

    def draw(self):

        mouse_pos = pygame.mouse.get_pos()

        self.renderer.draw_background()

        self.renderer.draw_board()

        self.renderer.draw_sidebar()

        self.renderer.draw_pieces(self.board)

        # Title
        title = self.font.render(
            "CARO AI",
            True,
            TEXT_COLOR
        )

        self.screen.blit(title, (780, 60))

        # AI mode
        ai_text = self.font.render(
            f"AI: {self.ai_mode}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(ai_text, (self.sidebar_x, 110))

        # Turn
        turn_text = self.font.render(
            f"Turn: {self.current_player}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(turn_text, (self.sidebar_x, 140))

        # Statistics
        nodes_text = self.font.render(
            f"Nodes: {self.nodes_searched}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(nodes_text, (self.sidebar_x, 400))

        score_text = self.font.render(
            f"Score: {self.ai_score}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(score_text, (self.sidebar_x, 440))

        time_text = self.font.render(
            f"Time: {self.ai_time}s",
            True,
            TEXT_COLOR
        )

        self.screen.blit(time_text, (self.sidebar_x, 480))

        # Buttons
        self.renderer.draw_button(
            self.undo_button,
            "Undo",
            self.font,
            mouse_pos
        )

        self.renderer.draw_button(
            self.redo_button,
            "Redo",
            self.font,
            mouse_pos
        )

        self.renderer.draw_button(
            self.reset_button,
            "Reset",
            self.font,
            mouse_pos
        )

        self.renderer.draw_button(
            self.home_button,
            "Home",
            self.font,
            mouse_pos
        )

        if self.ai_thinking:
            # Dark overlay on board
            overlay = pygame.Surface(
                (
                    BOARD_SIZE * CELL_SIZE,
                    BOARD_SIZE * CELL_SIZE
                )
            )

            overlay.set_alpha(140)

            overlay.fill((0, 0, 0))

            self.screen.blit(
                overlay,
                (BOARD_OFFSET_X, BOARD_OFFSET_Y)
            )

            # Popup
            popup_rect = pygame.Rect(
                250,
                250,
                350,
                150
            )

            pygame.draw.rect(
                self.screen,
                (50, 50, 50),
                popup_rect,
                border_radius=16
            )

            pygame.draw.rect(
                self.screen,
                (120, 120, 120),
                popup_rect,
                width=2,
                border_radius=16
            )

            # Text
            thinking_text = self.font.render(
                "AI THINKING...",
                True,
                (255, 220, 120)
            )

            text_rect = thinking_text.get_rect(
                center=(425, 325)
            )

            self.screen.blit(
                thinking_text,
                text_rect
            )

        # Game over
        if self.game_over:

            # Dark overlay only on board
            overlay = pygame.Surface(
                (BOARD_SIZE * CELL_SIZE,
                 BOARD_SIZE * CELL_SIZE)
            )

            overlay.set_alpha(140)

            overlay.fill((0, 0, 0))

            self.screen.blit(
                overlay,
                (BOARD_OFFSET_X, BOARD_OFFSET_Y)
            )

            # Popup box
            popup_rect = pygame.Rect(
                250,
                250,
                350,
                150
            )

            pygame.draw.rect(
                self.screen,
                (50, 50, 50),
                popup_rect,
                border_radius=16
            )

            pygame.draw.rect(
                self.screen,
                (120, 120, 120),
                popup_rect,
                width=2,
                border_radius=16
            )

            # Text
            if self.winner:
                text = f"{self.winner} Wins!"
            else:
                text = "Draw!"

            result_text = self.font.render(
                text,
                True,
                (255, 255, 255)
            )

            rect = result_text.get_rect(
                center=(425, 325)
            )

            self.screen.blit(result_text, rect)

            sub_text = self.font.render(
                "Use Reset or Home",
                True,
                (180, 180, 180)
            )

            sub_rect = sub_text.get_rect(
                center=(425, 360)
            )

            self.screen.blit(sub_text, sub_rect)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            # Home
            if self.home_button.collidepoint((mouse_x, mouse_y)):
                return HOME_SCREEN

            # Undo
            # Undo
            if self.undo_button.collidepoint((mouse_x, mouse_y)):

                # Undo AI move
                self.history.undo(self.board)

                # Undo player move
                player = self.history.undo(self.board)

                if player:
                    self.current_player = PLAYER_X

                    self.game_over = False
                    self.winner = None

            # Redo
            elif self.redo_button.collidepoint((mouse_x, mouse_y)):

                # Redo player move
                self.history.redo(self.board)

                # Redo AI move
                player = self.history.redo(self.board)

                if player:
                    self.current_player = PLAYER_X

            # Reset
            elif self.reset_button.collidepoint((mouse_x, mouse_y)):

                self.reset_game()

            # Board click
            elif (
                not self.game_over
                and
                BOARD_OFFSET_X <= mouse_x <= BOARD_OFFSET_X + BOARD_SIZE * CELL_SIZE
                and
                BOARD_OFFSET_Y <= mouse_y <= BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE
            ):

                col = (mouse_x - BOARD_OFFSET_X) // CELL_SIZE
                row = (mouse_y - BOARD_OFFSET_Y) // CELL_SIZE

                if self.board[row][col] == EMPTY:

                    self.board[row][col] = self.current_player

                    self.history.add_move(
                        row,
                        col,
                        self.current_player
                    )

                    # Check win
                    if GameLogic.check_win(
                        self.board,
                        self.current_player
                    ):

                        self.game_over = True
                        self.winner = self.current_player

                    elif GameLogic.check_draw(self.board):

                        self.game_over = True
                        self.winner = None

                    else:

                        self.current_player = PLAYER_O

                        self.ai_move()

        return GAME_SCREEN

    def ai_move(self):

        if self.game_over:
            return

        import time

        # Show thinking overlay
        self.ai_thinking = True

        self.draw()

        pygame.display.flip()

        start_time = time.time()

        # =========================
        # AI SEARCH
        # =========================

        if self.ai_mode == MINIMAX:

            move, score = MinimaxAI.get_best_move(
                self.board,
                depth=3
            )

            self.nodes_searched = (
                MinimaxAI.nodes_searched
            )

        else:

            move, score = AlphaBetaAI.get_best_move(
                self.board,
                depth=3
            )

            self.nodes_searched = (
                AlphaBetaAI.nodes_searched
            )

        end_time = time.time()

        self.ai_time = round(
            end_time - start_time,
            4
        )

        self.ai_score = score

        # Hide thinking overlay
        self.ai_thinking = False

        if move is None:
            return

        row, col = move

        self.board[row][col] = PLAYER_O

        self.history.add_move(
            row,
            col,
            PLAYER_O
        )

        # =========================
        # CHECK GAME STATE
        # =========================

        if GameLogic.check_win(
                self.board,
                PLAYER_O
        ):

            self.game_over = True
            self.winner = PLAYER_O

        elif GameLogic.check_draw(
                self.board
        ):

            self.game_over = True
            self.winner = None

        else:

            self.current_player = PLAYER_X