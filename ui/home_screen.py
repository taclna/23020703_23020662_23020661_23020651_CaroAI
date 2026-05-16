import pygame

from core.constants import *


class HomeScreen:

    def __init__(self, screen, font, big_font):

        self.screen   = screen
        self.font     = font
        self.big_font = big_font

        self.selected_ai = MINIMAX

        cx = WINDOW_WIDTH // 2

        # ── AI option cards (side by side) ──────────────────────────
        card_w, card_h = 200, 90
        gap = 20
        total = card_w * 2 + gap
        left  = cx - total // 2

        self.minimax_button   = pygame.Rect(left,           310, card_w, card_h)
        self.alphabeta_button = pygame.Rect(left + card_w + gap, 310, card_w, card_h)

        # ── Action buttons ───────────────────────────────────────────
        btn_w, btn_h = 420, 52

        self.start_button   = pygame.Rect(cx - btn_w // 2, 440, btn_w, btn_h)
        self.compare_button = pygame.Rect(cx - btn_w // 2, 524, btn_w, btn_h)

    # ─────────────────────────────────────────────────────────────────

    def draw(self):

        self.screen.fill(BG_COLOR)

        cx = WINDOW_WIDTH // 2

        # ── Thin top accent bar ──────────────────────────────────────
        pygame.draw.rect(self.screen, BTN_AI_SELECTED,
                         pygame.Rect(0, 0, WINDOW_WIDTH, 4))

        # ── Title ────────────────────────────────────────────────────
        title = self.big_font.render("CARO AI", True, TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(cx, 120)))

        # ── Subtitle ─────────────────────────────────────────────────
        sub = self.font.render("Select AI algorithm to play against", True, TEXT_DIM)
        self.screen.blit(sub, sub.get_rect(center=(cx, 168)))

        # ── Divider ──────────────────────────────────────────────────
        pygame.draw.line(self.screen, GRID_COLOR,
                         (cx - 160, 200), (cx + 160, 200), 1)

        # ── Section label ────────────────────────────────────────────
        lbl = self.font.render("AI MODE", True, TEXT_DIM)
        self.screen.blit(lbl, lbl.get_rect(center=(cx, 270)))

        # ── AI cards ─────────────────────────────────────────────────
        self._draw_ai_card(
            self.minimax_button,
            "Minimax",
            "Exhaustive search",
            self.selected_ai == MINIMAX
        )

        self._draw_ai_card(
            self.alphabeta_button,
            "Alpha-Beta",
            "Pruned search",
            self.selected_ai == ALPHABETA
        )

        # ── Play vs AI ───────────────────────────────────────────────
        ai_name = "Minimax" if self.selected_ai == MINIMAX else "Alpha-Beta"
        self._draw_primary_btn(
            self.start_button,
            f"Play vs {ai_name}",
            BTN_START
        )

        # ── Divider before compare ───────────────────────────────────
        pygame.draw.line(self.screen, GRID_COLOR,
                         (cx - 160, 506), (cx + 160, 506), 1)

        # ── Compare ──────────────────────────────────────────────────
        self._draw_primary_btn(
            self.compare_button,
            "Compare Both AIs",
            BTN_COMPARE
        )

    # ─────────────────────────────────────────────────────────────────

    def _draw_ai_card(self, rect, name, desc, selected):
        """Vertical card with name + description line."""

        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)

        # Background
        if selected:
            bg = BTN_AI_SELECTED
        elif hovered:
            bg = BUTTON_HOVER
        else:
            bg = BUTTON_COLOR

        pygame.draw.rect(self.screen, bg, rect, border_radius=14)

        # Selected indicator: left accent bar
        if selected:
            bar = pygame.Rect(rect.x, rect.y + 14, 4, rect.height - 28)
            pygame.draw.rect(self.screen, (255, 255, 255), bar, border_radius=2)

        # Border when not selected
        if not selected:
            pygame.draw.rect(self.screen, GRID_COLOR, rect, width=1, border_radius=14)

        # Name
        name_col = (255, 255, 255) if selected else TEXT_COLOR
        name_surf = self.font.render(name, True, name_col)
        self.screen.blit(name_surf, name_surf.get_rect(
            center=(rect.centerx, rect.centery - 12)))

        # Description
        desc_col = (210, 225, 255) if selected else TEXT_DIM
        # Use a slightly smaller surface by scaling font manually via render
        desc_surf = self.font.render(desc, True, desc_col)
        # Scale down 80 %
        sw = int(desc_surf.get_width() * 0.78)
        sh = int(desc_surf.get_height() * 0.78)
        desc_small = pygame.transform.smoothscale(desc_surf, (sw, sh))
        self.screen.blit(desc_small, desc_small.get_rect(
            center=(rect.centerx, rect.centery + 16)))

    def _draw_primary_btn(self, rect, text, color):

        mouse = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse)

        # Slightly lighten on hover
        if hovered:
            r = min(color[0] + 20, 255)
            g = min(color[1] + 20, 255)
            b = min(color[2] + 20, 255)
            bg = (r, g, b)
        else:
            bg = color

        pygame.draw.rect(self.screen, bg, rect, border_radius=12)

        label = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    # ─────────────────────────────────────────────────────────────────

    def handle_event(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            pos = event.pos

            if self.minimax_button.collidepoint(pos):
                self.selected_ai = MINIMAX
                return HOME_SCREEN

            elif self.alphabeta_button.collidepoint(pos):
                self.selected_ai = ALPHABETA
                return HOME_SCREEN

            elif self.start_button.collidepoint(pos):
                return GAME_SCREEN

            elif self.compare_button.collidepoint(pos):
                return COMPARE_SCREEN

        return HOME_SCREEN