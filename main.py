import pygame

from core.constants import *

from ui.home_screen import HomeScreen
from ui.game_screen import GameScreen


pygame.init()

screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

pygame.display.set_caption("Caro AI")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 54, bold=True)

# Screens
home_screen = HomeScreen(screen, font, big_font)

game_screen = GameScreen(
    screen,
    font,
    home_screen.selected_ai
)
current_screen = HOME_SCREEN

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if current_screen == HOME_SCREEN:

            next_screen = home_screen.handle_event(event)

            if next_screen == GAME_SCREEN:
                game_screen = GameScreen(
                    screen,
                    font,
                    home_screen.selected_ai
                )

                current_screen = GAME_SCREEN

        elif current_screen == GAME_SCREEN:

            next_screen = game_screen.handle_event(event)

            if next_screen == HOME_SCREEN:

                current_screen = HOME_SCREEN

    # Draw
    if current_screen == HOME_SCREEN:
        home_screen.draw()

    elif current_screen == GAME_SCREEN:
        game_screen.draw()

    pygame.display.update()

    clock.tick(60)

pygame.quit()