"""
store.py
========
The in-game tower store panel drawn on the right side of the screen.

Responsibilities
----------------
- Define TOWER_CATALOG: the ordered list of tower classes available to buy.
- Draw a card for each tower showing its name, cost, stats, and color swatch.
- Track which card the player has selected (highlighted card = active tower).
- Expose `selected_tower_class` so the Game knows what to place on click.

HOW TO ADD A NEW TOWER TO THE STORE
------------------------------------
1. Create the tower class in towers.py (follow the template there).
2. Import it here.
3. Append it to TOWER_CATALOG below.
Done — a new card will appear in the panel automatically.
"""

import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STORE_WIDTH, MAP_WIDTH,
    COLOR_STORE_BG, COLOR_STORE_BORDER,
    COLOR_CARD_BG, COLOR_CARD_HOVER, COLOR_CARD_SEL,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_GOLD,
)

# Import every tower class that should appear in the store.
# ── ADD NEW IMPORTS HERE ──────────────────────────────────────────────────
from towers import BasicTower, SniperTower, RapidTower
# ─────────────────────────────────────────────────────────────────────────

# TOWER_CATALOG controls the order cards appear in the panel.
# ── ADD NEW TOWER CLASSES HERE ────────────────────────────────────────────
TOWER_CATALOG = [
    BasicTower,
    SniperTower,
    RapidTower,
]
# ─────────────────────────────────────────────────────────────────────────

# Layout constants for the store panel
_PANEL_X     = MAP_WIDTH          # left edge of the panel
_CARD_MARGIN = 10                 # gap between cards and panel edges
_CARD_HEIGHT = 110                # height of each tower card
_CARD_WIDTH  = STORE_WIDTH - _CARD_MARGIN * 2
_SWATCH_SIZE = 24                 # colored box representing the tower


class Store:
    """
    Draws the store panel and handles card selection.

    Usage (in Game):
        self.store = Store()
        ...
        # in handle_events:
        self.store.handle_event(event)
        # in update:
        gold_display = self.gold
        # in draw:
        self.store.draw(self.screen, self.gold)
        # when placing a tower:
        TowerClass = self.store.selected_tower_class
        if TowerClass and self.gold >= TowerClass.DATA["cost"]:
            ...place tower...
    """

    def __init__(self):
        self.font_title = pygame.font.SysFont(None, 22)
        self.font_body  = pygame.font.SysFont(None, 18)
        self.font_cost  = pygame.font.SysFont(None, 20)

        # Which tower class is currently selected (None = nothing selected)
        self.selected_tower_class = None

        # Pre-compute the pygame.Rect for each card so hit-testing is cheap
        self._card_rects = self._build_card_rects()

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _build_card_rects(self):
        """Return a list of pygame.Rect, one per tower in TOWER_CATALOG."""
        rects = []
        for i in range(len(TOWER_CATALOG)):
            x = _PANEL_X + _CARD_MARGIN
            y = 50 + i * (_CARD_HEIGHT + _CARD_MARGIN)   # 50 px header gap
            rects.append(pygame.Rect(x, y, _CARD_WIDTH, _CARD_HEIGHT))
        return rects

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event):
        """
        Call this from Game.handle_events() for every pygame event.
        Handles left-click to select / deselect a tower card.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self._card_rects):
                if rect.collidepoint(mx, my):
                    cls = TOWER_CATALOG[i]
                    # Clicking the already-selected card deselects it
                    if self.selected_tower_class is cls:
                        self.selected_tower_class = None
                    else:
                        self.selected_tower_class = cls
                    return   # click was handled by the store

    def click_was_in_store(self, pos):
        """Return True if the given pixel position is inside the store panel."""
        return pos[0] >= _PANEL_X

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, surface, gold):
        """
        Render the full store panel.

        Args:
            surface : pygame.Surface to draw onto
            gold    : int current player gold (shown on each card if too poor)
        """
        # Panel background
        panel_rect = pygame.Rect(_PANEL_X, 0, STORE_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, COLOR_STORE_BG, panel_rect)
        # Left border line
        pygame.draw.line(surface, COLOR_STORE_BORDER,
                         (_PANEL_X, 0), (_PANEL_X, SCREEN_HEIGHT), 2)

        # Header
        header = self.font_title.render("TOWER STORE", True, COLOR_TEXT)
        surface.blit(header, (_PANEL_X + _CARD_MARGIN, 14))

        gold_surf = self.font_cost.render(f"Gold: {gold}", True, COLOR_GOLD)
        surface.blit(gold_surf, (_PANEL_X + _CARD_MARGIN, 32))

        # Cards
        mx, my = pygame.mouse.get_pos()
        for i, (cls, rect) in enumerate(zip(TOWER_CATALOG, self._card_rects)):
            self._draw_card(surface, cls, rect, gold, mx, my)

        # Bottom hint
        hint = self.font_body.render("Click card, then map", True, COLOR_TEXT_DIM)
        surface.blit(hint, (_PANEL_X + 6, SCREEN_HEIGHT - 20))

    def _draw_card(self, surface, tower_cls, rect, gold, mx, my):
        """Draw a single tower card."""
        data = tower_cls.DATA
        is_selected = (self.selected_tower_class is tower_cls)
        is_hovered  = rect.collidepoint(mx, my)
        can_afford  = gold >= data["cost"]

        # Card background
        if is_selected:
            bg = COLOR_CARD_SEL
        elif is_hovered:
            bg = COLOR_CARD_HOVER
        else:
            bg = COLOR_CARD_BG
        pygame.draw.rect(surface, bg, rect, border_radius=6)

        # Outer border (brighter when selected)
        border_color = (120, 120, 200) if is_selected else (60, 60, 90)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=6)

        # Color swatch (small box showing the tower's color)
        swatch_rect = pygame.Rect(rect.x + 6, rect.y + 6, _SWATCH_SIZE, _SWATCH_SIZE)
        pygame.draw.rect(surface, data["color"], swatch_rect, border_radius=3)

        # Tower name
        name_surf = self.font_title.render(data["name"], True, COLOR_TEXT)
        surface.blit(name_surf, (rect.x + _SWATCH_SIZE + 12, rect.y + 6))

        # Cost  (red if the player can't afford it)
        cost_color = COLOR_GOLD if can_afford else (200, 80, 80)
        cost_surf  = self.font_cost.render(f"{data['cost']} g", True, cost_color)
        surface.blit(cost_surf, (rect.x + _SWATCH_SIZE + 12, rect.y + 24))

        # Description (word-wrapped manually to fit the card)
        desc_lines = self._wrap_text(data["description"], self.font_body, _CARD_WIDTH - 12)
        for j, line in enumerate(desc_lines):
            line_surf = self.font_body.render(line, True, COLOR_TEXT_DIM)
            surface.blit(line_surf, (rect.x + 6, rect.y + 44 + j * 16))

        # Quick stats row
        stats = (f"Rng:{data['range']}  "
                 f"Dmg:{data['damage']}  "
                 f"Spd:{data['fire_rate']}")
        stats_surf = self.font_body.render(stats, True, COLOR_TEXT_DIM)
        surface.blit(stats_surf, (rect.x + 6, rect.y + _CARD_HEIGHT - 18))

    @staticmethod
    def _wrap_text(text, font, max_width):
        """Break `text` into a list of lines that each fit within max_width."""
        words  = text.split()
        lines  = []
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