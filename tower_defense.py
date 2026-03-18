"""
tower_defense.py
================
Main entry point for the tower defense game.

This file owns the Game class and the main loop.  It deliberately contains
as little game-logic as possible — each concern lives in its own module:

    constants.py  — all magic numbers, colors, path data
    towers.py     — BaseTower, Projectile, and every tower subclass
    store.py      — the in-game store panel UI and TOWER_CATALOG

To run:
    pip install pygame
    python tower_defense.py
"""

import pygame
import sys
import math

# ---------------------------------------------------------------------------
# Local modules
# ---------------------------------------------------------------------------
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    MAP_WIDTH, STORE_WIDTH,
    CELL_SIZE, GRID_COLS, GRID_ROWS,
    COLOR_BG, COLOR_GRID, COLOR_PATH, COLOR_ENEMY,
    COLOR_TEXT, COLOR_TEXT_DIM, COLOR_GOLD,
    WAYPOINT_PIXELS, PATH_CELLS,
    ENEMY_SPEED, ENEMY_HEALTH, ENEMY_SIZE, ENEMY_SPAWN_RATE,
    STARTING_GOLD,
)
from towers import Projectile   # used only for type clarity; towers create them
from store  import Store


# ---------------------------------------------------------------------------
# Enemy
# ---------------------------------------------------------------------------

class Enemy:
    """
    Walks along WAYPOINT_PIXELS, takes damage from projectiles.
    Drawn as a simple colored box — replace with a sprite later.
    """

    def __init__(self):
        self.x, self.y  = WAYPOINT_PIXELS[0]
        self.health      = ENEMY_HEALTH
        self.max_health  = ENEMY_HEALTH
        self.speed       = ENEMY_SPEED
        self.size        = ENEMY_SIZE
        self.alive       = True
        self.reached_end = False
        self.waypoint_index = 1   # index of the *next* waypoint to head toward

    def update(self):
        if not self.alive or self.reached_end:
            return
        tx, ty = WAYPOINT_PIXELS[self.waypoint_index]
        dx, dy = tx - self.x, ty - self.y
        dist   = math.hypot(dx, dy)
        if dist <= self.speed:
            self.x, self.y = tx, ty
            self.waypoint_index += 1
            if self.waypoint_index >= len(WAYPOINT_PIXELS):
                self.reached_end = True
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        half = self.size // 2
        pygame.draw.rect(surface, COLOR_ENEMY,
                         pygame.Rect(self.x - half, self.y - half,
                                     self.size, self.size))
        # Health bar
        bw, bh = self.size, 4
        bx, by = self.x - half, self.y - half - 6
        ratio   = self.health / self.max_health
        pygame.draw.rect(surface, (80,  0, 0),  pygame.Rect(bx, by, bw, bh))
        pygame.draw.rect(surface, (0, 200, 80), pygame.Rect(bx, by, int(bw * ratio), bh))


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------

class Game:
    """
    Owns all game state and runs the main loop.

    Input flow  : handle_events → store.handle_event → _try_place_tower
    Update flow : _spawn_enemies → enemy.update → tower.update → proj.update
    Draw flow   : map/grid/path → towers → enemies → projectiles → HUD → store
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock  = pygame.time.Clock()
        self.font   = pygame.font.SysFont(None, 26)

        # Game objects
        self.enemies     = []
        self.towers      = []
        self.projectiles = []
        self.tower_cells = set()   # (col, row) cells that already hold a tower

        # Economy
        self.gold  = STARTING_GOLD
        self.score = 0
        self.lives = 20

        # Timers
        self.spawn_timer = 0

        # The store panel (handles its own drawing and card selection)
        self.store = Store()

        self.running = True

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Let the store handle clicks on its panel first.
                # If the click was inside the store, don't also place a tower.
                if self.store.click_was_in_store(event.pos):
                    self.store.handle_event(event)
                else:
                    self._try_place_tower(event.pos)

    def _try_place_tower(self, mouse_pos):
        """
        Place the selected tower on the clicked grid cell, if:
          - a tower class is selected in the store
          - the cell is not on the enemy path
          - the cell is not already occupied
          - the player has enough gold
        """
        TowerClass = self.store.selected_tower_class
        if TowerClass is None:
            return   # nothing selected — ignore the click

        col = mouse_pos[0] // CELL_SIZE
        row = mouse_pos[1] // CELL_SIZE

        # Guard: must be within the map grid (not the store panel)
        if col >= GRID_COLS or row >= GRID_ROWS:
            return
        if (col, row) in PATH_CELLS:
            return
        if (col, row) in self.tower_cells:
            return

        cost = TowerClass.DATA["cost"]
        if self.gold < cost:
            return   # player can't afford it

        # All checks passed — place the tower and deduct gold
        self.towers.append(TowerClass(col, row))
        self.tower_cells.add((col, row))
        self.gold -= cost

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self):
        self._spawn_enemies()
        self._update_enemies()
        self._update_towers()
        self._update_projectiles()
        self._cleanup()

    def _spawn_enemies(self):
        self.spawn_timer += 1
        if self.spawn_timer >= ENEMY_SPAWN_RATE:
            self.spawn_timer = 0
            self.enemies.append(Enemy())

    def _update_enemies(self):
        for enemy in self.enemies:
            enemy.update()
            if enemy.reached_end:
                self.lives -= 1
                enemy.alive = False

    def _update_towers(self):
        # Each tower receives the enemy list and appends its own projectiles
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

    def _update_projectiles(self):
        for proj in self.projectiles:
            proj.update()

    def _cleanup(self):
        """Remove dead enemies and spent projectiles; award gold for kills."""
        for e in self.enemies:
            if not e.alive and not e.reached_end:
                # Reward: 10 gold + 1 score point per kill
                self.gold  += 10
                self.score += 10
        self.enemies     = [e for e in self.enemies     if e.alive]
        self.projectiles = [p for p in self.projectiles if p.active]

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self):
        self.screen.fill(COLOR_BG)
        self._draw_grid()
        self._draw_path()
        for tower in self.towers:
            tower.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for proj in self.projectiles:
            proj.draw(self.screen)
        self._draw_hud()
        self.store.draw(self.screen, self.gold)   # store is drawn on top / last
        pygame.display.flip()

    def _draw_grid(self):
        """Faint grid lines across the map area only (not the store panel)."""
        for col in range(GRID_COLS + 1):
            x = col * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
        for row in range(GRID_ROWS + 1):
            y = row * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (MAP_WIDTH, y))

    def _draw_path(self):
        for col, row in PATH_CELLS:
            pygame.draw.rect(self.screen, COLOR_PATH,
                             pygame.Rect(col * CELL_SIZE, row * CELL_SIZE,
                                         CELL_SIZE, CELL_SIZE))

    def _draw_hud(self):
        """Score, lives, and gold in the top-left corner of the map."""
        y = 6
        for text, color in [
            (f"Score: {self.score}", COLOR_TEXT),
            (f"Lives: {self.lives}", COLOR_TEXT),
            (f"Gold:  {self.gold}",  COLOR_GOLD),
        ]:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (8, y))
            y += 22

        # Show selected tower name below stats
        if self.store.selected_tower_class:
            name = self.store.selected_tower_class.DATA["name"]
            hint = self.font.render(f"Placing: {name}", True, (180, 220, 255))
            self.screen.blit(hint, (8, y + 4))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()