import pygame
from constants import (
    SCREEN_HEIGHT,
    STORE_WIDTH,
    MAP_WIDTH,
    COLOR_STORE_BG,
    COLOR_STORE_BORDER,
    COLOR_CARD_BG,
    COLOR_CARD_HOVER,
    COLOR_CARD_SEL,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_GOLD,
)

from towers import (
    BasicTower,
    SniperTower,
    RapidTower,
    SlowTower,
    SplashTower,
)

TOWER_CATALOG = [
    BasicTower,
    SniperTower,
    RapidTower,
    SlowTower,
    SplashTower,
]

_PANEL_X = MAP_WIDTH
_CARD_MARGIN = 10
_CARD_HEIGHT = 110
_CARD_WIDTH = STORE_WIDTH - _CARD_MARGIN * 2
_SWATCH_SIZE = 24


class Store:
    def __init__(self):
        self.font_title = pygame.font.SysFont(None, 22)
        self.font_body = pygame.font.SysFont(None, 18)
        self.font_cost = pygame.font.SysFont(None, 20)

        self.selected_tower_class = None
        self._card_rects = self._build_card_rects()

    def _build_card_rects(self):
        rects = []
        for i in range(len(TOWER_CATALOG)):
            x = _PANEL_X + _CARD_MARGIN
            y = 50 + i * (_CARD_HEIGHT + _CARD_MARGIN)
            rects.append(pygame.Rect(x, y, _CARD_WIDTH, _CARD_HEIGHT))
        return rects

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self._card_rects):
                if rect.collidepoint(mx, my):
                    cls = TOWER_CATALOG[i]
                    if self.selected_tower_class is cls:
                        self.selected_tower_class = None
                    else:
                        self.selected_tower_class = cls
                    return

    def click_was_in_store(self, pos):
        return pos[0] >= _PANEL_X

    def draw(self, surface, gold):
        panel_rect = pygame.Rect(_PANEL_X, 0, STORE_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, COLOR_STORE_BG, panel_rect)
        pygame.draw.line(surface, COLOR_STORE_BORDER, (_PANEL_X, 0), (_PANEL_X, SCREEN_HEIGHT), 2)

        header = self.font_title.render("TOWER STORE", True, COLOR_TEXT)
        surface.blit(header, (_PANEL_X + _CARD_MARGIN, 14))

        gold_surf = self.font_cost.render(f"Gold: {gold}", True, COLOR_GOLD)
        surface.blit(gold_surf, (_PANEL_X + _CARD_MARGIN, 32))

        mx, my = pygame.mouse.get_pos()
        for cls, rect in zip(TOWER_CATALOG, self._card_rects):
            self._draw_card(surface, cls, rect, gold, mx, my)

        hint = self.font_body.render("U=upgrade S=sell", True, COLOR_TEXT_DIM)
        surface.blit(hint, (_PANEL_X + 6, SCREEN_HEIGHT - 20))

    def _draw_card(self, surface, tower_cls, rect, gold, mx, my):
        data = tower_cls.DATA
        is_selected = self.selected_tower_class is tower_cls
        is_hovered = rect.collidepoint(mx, my)
        can_afford = gold >= data["cost"]

        if is_selected:
            bg = COLOR_CARD_SEL
        elif is_hovered:
            bg = COLOR_CARD_HOVER
        else:
            bg = COLOR_CARD_BG

        pygame.draw.rect(surface, bg, rect, border_radius=6)
        border_color = (120, 120, 200) if is_selected else (60, 60, 90)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=6)

        swatch_rect = pygame.Rect(rect.x + 6, rect.y + 6, _SWATCH_SIZE, _SWATCH_SIZE)
        pygame.draw.rect(surface, data["color"], swatch_rect, border_radius=3)

        name_surf = self.font_title.render(data["name"], True, COLOR_TEXT)
        surface.blit(name_surf, (rect.x + _SWATCH_SIZE + 12, rect.y + 6))

        cost_color = COLOR_GOLD if can_afford else (200, 80, 80)
        cost_surf = self.font_cost.render(f"{data['cost']} g", True, cost_color)
        surface.blit(cost_surf, (rect.x + _SWATCH_SIZE + 12, rect.y + 24))

        desc_lines = self._wrap_text(data["description"], self.font_body, _CARD_WIDTH - 12)
        for j, line in enumerate(desc_lines):
            line_surf = self.font_body.render(line, True, COLOR_TEXT_DIM)
            surface.blit(line_surf, (rect.x + 6, rect.y + 44 + j * 16))

        stats = f"Rng:{data['range']}  Dmg:{data['damage']}  Spd:{data['fire_rate']}"
        stats_surf = self.font_body.render(stats, True, COLOR_TEXT_DIM)
        surface.blit(stats_surf, (rect.x + 6, rect.y + _CARD_HEIGHT - 18))

    @staticmethod
    def _wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

        return lines