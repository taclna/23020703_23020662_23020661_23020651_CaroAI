import pygame
import time

from core.constants import *

from core.game_logic import GameLogic

from ai.minimax import MinimaxAI
from ai.alphabeta import AlphaBetaAI


class CompareScreen:

    def __init__(self, screen, font):

        self.screen = screen
        self.font = font

        self.cell_size = 40

        self.board_size_px = (
            BOARD_SIZE * self.cell_size
        )

        # Left board position
        self.left_x = 40
        self.left_y = 120

        # Right board position
        self.right_x = 620
        self.right_y = 120

        # Boards
        self.board_minimax = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.board_alphabeta = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        # Statistics
        self.minimax_nodes = 0
        self.minimax_time = 0
        self.minimax_score = 0

        self.alphabeta_nodes = 0
        self.alphabeta_time = 0
        self.alphabeta_score = 0

        # Game state
        self.game_over = False

        self.winner_minimax = None
        self.winner_alphabeta = None

        # Buttons
        self.home_button = pygame.Rect(
            1120,
            620,
            180,
            50
        )

        self.reset_button = pygame.Rect(
            900,
            620,
            180,
            50
        )

    def reset_game(self):

        self.board_minimax = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.board_alphabeta = [
            [EMPTY for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]

        self.minimax_nodes = 0
        self.minimax_time = 0
        self.minimax_score = 0

        self.alphabeta_nodes = 0
        self.alphabeta_time = 0
        self.alphabeta_score = 0

        self.game_over = False

        self.winner_minimax = None
        self.winner_alphabeta = None

    def draw(self):

        self.screen.fill(BG_COLOR)

        # Titles
        left_title = self.font.render(
            "MINIMAX",
            True,
            TEXT_COLOR
        )

        self.screen.blit(left_title, (170, 50))

        right_title = self.font.render(
            "ALPHA-BETA",
            True,
            TEXT_COLOR
        )

        self.screen.blit(right_title, (760, 50))

        # Draw boards
        self.draw_board(
            self.board_minimax,
            self.left_x,
            self.left_y
        )

        self.draw_board(
            self.board_alphabeta,
            self.right_x,
            self.right_y
        )

        # Stats minimax
        self.draw_stats(
            x=40,
            y=520,
            nodes=self.minimax_nodes,
            score=self.minimax_score,
            thinking_time=self.minimax_time
        )

        # Stats alphabeta
        self.draw_stats(
            x=620,
            y=520,
            nodes=self.alphabeta_nodes,
            score=self.alphabeta_score,
            thinking_time=self.alphabeta_time
        )

        # Buttons
        mouse_pos = pygame.mouse.get_pos()

        self.draw_button(
            self.reset_button,
            "Reset",
            mouse_pos
        )

        self.draw_button(
            self.home_button,
            "Home",
            mouse_pos
        )

        # Winner text
        if self.winner_minimax:

            text = self.font.render(
                f"Winner: {self.winner_minimax}",
                True,
                (255, 200, 80)
            )

            self.screen.blit(text, (140, 470))

        if self.winner_alphabeta:

            text = self.font.render(
                f"Winner: {self.winner_alphabeta}",
                True,
                (255, 200, 80)
            )

            self.screen.blit(text, (720, 470))

    def draw_board(self, board, start_x, start_y):

        # Grid
        for i in range(BOARD_SIZE + 1):

            # Vertical
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (
                    start_x + i * self.cell_size,
                    start_y
                ),
                (
                    start_x + i * self.cell_size,
                    start_y + self.board_size_px
                ),
                2
            )

            # Horizontal
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (
                    start_x,
                    start_y + i * self.cell_size
                ),
                (
                    start_x + self.board_size_px,
                    start_y + i * self.cell_size
                ),
                2
            )

        # Pieces
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                value = board[row][col]

                center_x = (
                    start_x
                    + col * self.cell_size
                    + self.cell_size // 2
                )

                center_y = (
                    start_y
                    + row * self.cell_size
                    + self.cell_size // 2
                )

                # Draw X
                if value == PLAYER_X:

                    offset = 12

                    pygame.draw.line(
                        self.screen,
                        X_COLOR,
                        (
                            center_x - offset,
                            center_y - offset
                        ),
                        (
                            center_x + offset,
                            center_y + offset
                        ),
                        3
                    )

                    pygame.draw.line(
                        self.screen,
                        X_COLOR,
                        (
                            center_x + offset,
                            center_y - offset
                        ),
                        (
                            center_x - offset,
                            center_y + offset
                        ),
                        3
                    )

                # Draw O
                elif value == PLAYER_O:

                    pygame.draw.circle(
                        self.screen,
                        O_COLOR,
                        (
                            center_x,
                            center_y
                        ),
                        13,
                        3
                    )

    def draw_stats(
        self,
        x,
        y,
        nodes,
        score,
        thinking_time
    ):

        nodes_text = self.font.render(
            f"Nodes: {nodes}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(nodes_text, (x, y))

        score_text = self.font.render(
            f"Score: {score}",
            True,
            TEXT_COLOR
        )

        self.screen.blit(score_text, (x, y + 35))

        time_text = self.font.render(
            f"Time: {thinking_time}s",
            True,
            TEXT_COLOR
        )

        self.screen.blit(time_text, (x, y + 70))

    def draw_button(
        self,
        rect,
        text,
        mouse_pos
    ):

        color = BUTTON_COLOR

        if rect.collidepoint(mouse_pos):
            color = BUTTON_HOVER

        pygame.draw.rect(
            self.screen,
            color,
            rect,
            border_radius=12
        )

        label = self.font.render(
            text,
            True,
            TEXT_COLOR
        )

        label_rect = label.get_rect(
            center=rect.center
        )

        self.screen.blit(label, label_rect)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos

            # Home
            if self.home_button.collidepoint(
                (mouse_x, mouse_y)
            ):
                return HOME_SCREEN

            # Reset
            if self.reset_button.collidepoint(
                (mouse_x, mouse_y)
            ):

                self.reset_game()

            # Click LEFT BOARD ONLY
            elif (
                self.left_x
                <= mouse_x
                <= self.left_x + self.board_size_px
                and
                self.left_y
                <= mouse_y
                <= self.left_y + self.board_size_px
                and
                not self.game_over
            ):

                col = (
                    mouse_x - self.left_x
                ) // self.cell_size

                row = (
                    mouse_y - self.left_y
                ) // self.cell_size

                # Empty cell
                if (
                    self.board_minimax[row][col]
                    == EMPTY
                ):

                    # PLAYER MOVE
                    self.board_minimax[row][col] = PLAYER_X

                    self.board_alphabeta[row][col] = PLAYER_X

                    # Check player win
                    if GameLogic.check_win(
                        self.board_minimax,
                        PLAYER_X
                    ):

                        self.winner_minimax = PLAYER_X
                        self.winner_alphabeta = PLAYER_X

                        self.game_over = True

                        return COMPARE_SCREEN

                    # =====================
                    # MINIMAX
                    # =====================

                    start = time.time()

                    move1, score1 = (
                        MinimaxAI.get_best_move(
                            self.board_minimax,
                            depth=3
                        )
                    )

                    end = time.time()

                    self.minimax_time = round(
                        end - start,
                        4
                    )

                    self.minimax_nodes = (
                        MinimaxAI.nodes_searched
                    )

                    self.minimax_score = score1

                    if move1:

                        r1, c1 = move1

                        self.board_minimax[r1][c1] = PLAYER_O

                        if GameLogic.check_win(
                            self.board_minimax,
                            PLAYER_O
                        ):

                            self.winner_minimax = PLAYER_O

                    # =====================
                    # ALPHA BETA
                    # =====================

                    start = time.time()

                    move2, score2 = (
                        AlphaBetaAI.get_best_move(
                            self.board_alphabeta,
                            depth=3
                        )
                    )

                    end = time.time()

                    self.alphabeta_time = round(
                        end - start,
                        4
                    )

                    self.alphabeta_nodes = (
                        AlphaBetaAI.nodes_searched
                    )

                    self.alphabeta_score = score2

                    if move2:

                        r2, c2 = move2

                        self.board_alphabeta[r2][c2] = PLAYER_O

                        if GameLogic.check_win(
                            self.board_alphabeta,
                            PLAYER_O
                        ):

                            self.winner_alphabeta = PLAYER_O

        return COMPARE_SCREEN