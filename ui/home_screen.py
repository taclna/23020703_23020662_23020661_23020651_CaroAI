import pygame

from core.constants import *


class HomeScreen:

    def __init__(self, screen, font, big_font):

        self.screen = screen
        self.font = font
        self.big_font = big_font

        self.selected_ai = MINIMAX

        button_width = 300
        button_height = 60

        center_x = WINDOW_WIDTH // 2 - button_width // 2

        self.minimax_button = pygame.Rect(
            center_x,
            250,
            button_width,
            button_height
        )

        self.alphabeta_button = pygame.Rect(
            center_x,
            340,
            button_width,
            button_height
        )

        self.compare_button = pygame.Rect(
            center_x,
            470,
            button_width,
            70
        )

    def draw(self):

        self.screen.fill(BG_COLOR)

        title = self.big_font.render(
            "CARO AI",
            True,
            TEXT_COLOR
        )

        self.screen.blit(title, (360, 100))


        self.draw_ai_button(
            self.minimax_button,
            "Minimax",
            self.selected_ai == MINIMAX
        )

        self.draw_ai_button(
            self.alphabeta_button,
            "Alpha-Beta Pruning",
            self.selected_ai == ALPHABETA
        )

        pygame.draw.rect(
            self.screen,
            (180, 120, 40),
            self.compare_button,
            border_radius=12
        )

        compare_text = self.font.render(
            "Compare Both AI",
            True,
            TEXT_COLOR
        )

        compare_rect = compare_text.get_rect(
            center=self.compare_button.center
        )

        self.screen.blit(compare_text, compare_rect)

    def draw_ai_button(self, rect, text, selected):

        color = (90, 90, 90)

        if selected:
            color = (70, 130, 220)

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

        label_rect = label.get_rect(center=rect.center)

        self.screen.blit(label, label_rect)

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            if self.minimax_button.collidepoint(mouse_pos):

                self.selected_ai = MINIMAX

                return GAME_SCREEN

            elif self.alphabeta_button.collidepoint(mouse_pos):

                self.selected_ai = ALPHABETA

                return GAME_SCREEN

            elif self.compare_button.collidepoint(mouse_pos):

                return COMPARE_SCREEN

        return HOME_SCREEN