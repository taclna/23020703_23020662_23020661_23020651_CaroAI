import pygame

from core.constants import *


class Renderer:

    def __init__(self, screen):
        self.screen = screen

    def draw_background(self):
        self.screen.fill(BG_COLOR)

    def draw_board(self):

        board_pixel_size = BOARD_SIZE * CELL_SIZE

        for i in range(BOARD_SIZE + 1):

            # Vertical
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y),
                (BOARD_OFFSET_X + i * CELL_SIZE,
                 BOARD_OFFSET_Y + board_pixel_size),
                2
            )

            # Horizontal
            pygame.draw.line(
                self.screen,
                GRID_COLOR,
                (BOARD_OFFSET_X,
                 BOARD_OFFSET_Y + i * CELL_SIZE),
                (BOARD_OFFSET_X + board_pixel_size,
                 BOARD_OFFSET_Y + i * CELL_SIZE),
                2
            )

    def draw_sidebar(self):

        sidebar_x = 700

        pygame.draw.rect(
            self.screen,
            SIDEBAR_COLOR,
            (sidebar_x, 0, 300, WINDOW_HEIGHT)
        )

    def draw_button(self, rect, text, font, mouse_pos):

        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_COLOR

        pygame.draw.rect(self.screen, color, rect, border_radius=10)

        text_surface = font.render(text, True, TEXT_COLOR)

        text_rect = text_surface.get_rect(center=rect.center)

        self.screen.blit(text_surface, text_rect)

    def draw_pieces(self, board):

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):

                value = board[row][col]

                center_x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
                center_y = BOARD_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2

                if value == PLAYER_X:

                    offset = 18

                    pygame.draw.line(
                        self.screen,
                        X_COLOR,
                        (center_x - offset, center_y - offset),
                        (center_x + offset, center_y + offset),
                        4
                    )

                    pygame.draw.line(
                        self.screen,
                        X_COLOR,
                        (center_x + offset, center_y - offset),
                        (center_x - offset, center_y + offset),
                        4
                    )

                elif value == PLAYER_O:

                    pygame.draw.circle(
                        self.screen,
                        O_COLOR,
                        (center_x, center_y),
                        20,
                        4
                    )