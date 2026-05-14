import pygame

from core.constants import *

from ui.home_screen import HomeScreen
from ui.game_screen import GameScreen
from ui.compare_screen import CompareScreen


pygame.init()

screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

pygame.display.set_caption("Caro AI")

clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)

big_font = pygame.font.SysFont(
    "arial",
    54,
    bold=True
)

# =========================
# Screens
# =========================

home_screen = HomeScreen(
    screen,
    font,
    big_font
)

game_screen = None

compare_screen = None

current_screen = HOME_SCREEN

# =========================
# Main Loop
# =========================

running = True

while running:

    for event in pygame.event.get():

        # Quit
        if event.type == pygame.QUIT:
            running = False

        # =========================
        # HOME SCREEN
        # =========================

        if current_screen == HOME_SCREEN:

            next_screen = (
                home_screen.handle_event(event)
            )

            # Single AI mode
            if next_screen == GAME_SCREEN:

                game_screen = GameScreen(
                    screen,
                    font,
                    home_screen.selected_ai
                )

                current_screen = GAME_SCREEN

            # Compare mode
            elif next_screen == COMPARE_SCREEN:

                compare_screen = CompareScreen(
                    screen,
                    font
                )

                current_screen = COMPARE_SCREEN

        # =========================
        # GAME SCREEN
        # =========================

        elif current_screen == GAME_SCREEN:

            next_screen = (
                game_screen.handle_event(event)
            )

            if next_screen == HOME_SCREEN:

                current_screen = HOME_SCREEN

        # =========================
        # COMPARE SCREEN
        # =========================

        elif current_screen == COMPARE_SCREEN:

            next_screen = (
                compare_screen.handle_event(event)
            )

            if next_screen == HOME_SCREEN:

                current_screen = HOME_SCREEN

    # =========================
    # DRAW
    # =========================

    if current_screen == HOME_SCREEN:

        home_screen.draw()

    elif current_screen == GAME_SCREEN:

        game_screen.draw()

    elif current_screen == COMPARE_SCREEN:

        compare_screen.draw()

    pygame.display.update()

    clock.tick(60)

pygame.quit()