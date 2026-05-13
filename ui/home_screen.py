import pygame

from core.constants import *


class HomeScreen:

    def __init__(self, screen, font, big_font):

        self.screen = screen
        self.font = font
        self.big_font = big_font

        self.selected_ai = MINIMAX

        self.minimax_button = pygame.Rect(350, 250, 300, 60)
        self.alphabeta_button = pygame.Rect(350, 340, 300, 60)

        self.start_button = pygame.Rect(350, 460, 300, 70)

    def draw(self):

        self.screen.fill(BG_COLOR)

        title = self.big_font.render(
            "CARO AI",
            True,
            TEXT_COLOR
        )

        self.screen.blit(title, (360, 100))

        subtitle = self.font.render(
            "Choose AI Algorithm",
            True,
            TEXT_COLOR
        )

        self.screen.blit(subtitle, (370, 190))

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
            (50, 140, 70),
            self.start_button,
            border_radius=12
        )

        start_text = self.font.render(
            "Start Game",
            True,
            TEXT_COLOR
        )

        start_rect = start_text.get_rect(
            center=self.start_button.center
        )

        self.screen.blit(start_text, start_rect)

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

            elif self.alphabeta_button.collidepoint(mouse_pos):
                self.selected_ai = ALPHABETA

            elif self.start_button.collidepoint(mouse_pos):
                return GAME_SCREEN

        return HOME_SCREEN