import pygame
import sys

from constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    MAP_WIDTH,
    CELL_SIZE,
    GRID_COLS,
    GRID_ROWS,
    COLOR_BG,
    COLOR_GRID,
    COLOR_PATH,
    COLOR_TEXT,
    COLOR_GOLD,
    PATH_CELLS,
    STARTING_GOLD,
    STARTING_LIVES,
    ENEMY_SPAWN_RATE,
    TIME_BETWEEN_WAVES,
    WAVES,
)
from store import Store
from enemies import BasicEnemy, FastEnemy, ArmoredEnemy, BossEnemy

ENEMY_TYPES = {
    "basic": BasicEnemy,
    "fast": FastEnemy,
    "armored": ArmoredEnemy,
    "boss": BossEnemy,
}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 26)
        self.big_font = pygame.font.SysFont(None, 40)

        self.enemies = []
        self.towers = []
        self.projectiles = []

        # map cell -> tower object
        self.tower_cells = {}

        self.gold = STARTING_GOLD
        self.score = 0
        self.lives = STARTING_LIVES

        self.spawn_timer = 0
        self.wave_number = 0
        self.wave_queue = []
        self.state = "intermission"
        self.intermission_timer = TIME_BETWEEN_WAVES

        self.selected_map_tower = None
        self.store = Store()
        self.running = True

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.state == "intermission":
                    self._start_next_wave()
                elif event.key == pygame.K_u:
                    self._upgrade_selected_tower()
                elif event.key == pygame.K_s:
                    self._sell_selected_tower()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.store.click_was_in_store(event.pos):
                    self.store.handle_event(event)
                else:
                    self._handle_map_click(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.selected_map_tower = None

    def _handle_map_click(self, mouse_pos):
        col = mouse_pos[0] // CELL_SIZE
        row = mouse_pos[1] // CELL_SIZE

        if col >= GRID_COLS or row >= GRID_ROWS:
            return

        if (col, row) in self.tower_cells:
            self.selected_map_tower = self.tower_cells[(col, row)]
            return

        self.selected_map_tower = None
        self._try_place_tower(mouse_pos)

    def _try_place_tower(self, mouse_pos):
        TowerClass = self.store.selected_tower_class
        if TowerClass is None:
            return

        col = mouse_pos[0] // CELL_SIZE
        row = mouse_pos[1] // CELL_SIZE

        if col >= GRID_COLS or row >= GRID_ROWS:
            return
        if (col, row) in PATH_CELLS:
            return
        if (col, row) in self.tower_cells:
            return

        cost = TowerClass.DATA["cost"]
        if self.gold < cost:
            return

        tower = TowerClass(col, row)
        self.towers.append(tower)
        self.tower_cells[(col, row)] = tower
        self.gold -= cost

    # ------------------------------------------------------------------
    # Waves
    # ------------------------------------------------------------------

    def _start_next_wave(self):
        if self.wave_number >= len(WAVES):
            self.state = "victory"
            return

        self.wave_number += 1
        self.wave_queue = self._build_wave_queue(WAVES[self.wave_number - 1])
        self.spawn_timer = 0
        self.state = "playing"

    def _build_wave_queue(self, wave_definition):
        queue = []
        for enemy_name, count in wave_definition:
            queue.extend([ENEMY_TYPES[enemy_name]] * count)
        return queue

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self):
        if self.state == "playing":
            self._spawn_enemies()
            self._update_enemies()
            self._update_towers()
            self._update_projectiles()
            self._cleanup()
            self._check_wave_finished()
            self._check_game_over()
        elif self.state == "intermission" and self.wave_number < len(WAVES):
            if self.intermission_timer > 0:
                self.intermission_timer -= 1

    def _spawn_enemies(self):
        self.spawn_timer += 1
        if self.wave_queue and self.spawn_timer >= ENEMY_SPAWN_RATE:
            self.spawn_timer = 0
            enemy_class = self.wave_queue.pop(0)
            self.enemies.append(enemy_class())

    def _update_enemies(self):
        for enemy in self.enemies:
            enemy.update()
            if enemy.reached_end:
                self.lives -= 1
                enemy.alive = False

    def _update_towers(self):
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)

    def _update_projectiles(self):
        for proj in self.projectiles:
            proj.update()

    def _cleanup(self):
        for e in self.enemies:
            if not e.alive and not e.reached_end:
                self.gold += e.reward
                self.score += e.reward

        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.active]

    def _check_wave_finished(self):
        if self.state == "playing" and not self.wave_queue and not self.enemies:
            if self.wave_number >= len(WAVES):
                self.state = "victory"
            else:
                self.state = "intermission"
                self.intermission_timer = TIME_BETWEEN_WAVES
                self.gold += 25 + self.wave_number * 10

    def _check_game_over(self):
        if self.lives <= 0:
            self.state = "game_over"

    # ------------------------------------------------------------------
    # Tower actions
    # ------------------------------------------------------------------

    def _upgrade_selected_tower(self):
        tower = self.selected_map_tower
        if tower and tower.can_upgrade():
            cost = tower.get_upgrade_cost()
            if self.gold >= cost:
                self.gold -= cost
                tower.upgrade()

    def _sell_selected_tower(self):
        tower = self.selected_map_tower
        if tower is None:
            return

        self.gold += tower.get_sell_value()
        self.towers.remove(tower)
        self.tower_cells.pop((tower.col, tower.row), None)
        self.selected_map_tower = None

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def draw(self):
        self.screen.fill(COLOR_BG)
        self._draw_grid()
        self._draw_path()
        self._draw_range_preview()

        for tower in self.towers:
            tower.draw(self.screen)

        if self.selected_map_tower:
            pygame.draw.circle(
                self.screen,
                (180, 220, 255),
                (self.selected_map_tower.x, self.selected_map_tower.y),
                self.selected_map_tower.range,
                1,
            )

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        self._draw_hud()
        self.store.draw(self.screen, self.gold)
        pygame.display.flip()

    def _draw_grid(self):
        for col in range(GRID_COLS + 1):
            x = col * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))

        for row in range(GRID_ROWS + 1):
            y = row * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (MAP_WIDTH, y))

    def _draw_path(self):
        for col, row in PATH_CELLS:
            pygame.draw.rect(
                self.screen,
                COLOR_PATH,
                pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )

    def _draw_range_preview(self):
        TowerClass = self.store.selected_tower_class
        if TowerClass is None:
            return

        mx, my = pygame.mouse.get_pos()
        if mx >= MAP_WIDTH:
            return

        col = mx // CELL_SIZE
        row = my // CELL_SIZE

        if col >= GRID_COLS or row >= GRID_ROWS:
            return

        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2

        is_valid = (
            (col, row) not in PATH_CELLS
            and (col, row) not in self.tower_cells
        )

        color = (80, 220, 120) if is_valid else (220, 80, 80)

        pygame.draw.rect(
            self.screen,
            color,
            pygame.Rect(col * CELL_SIZE + 2, row * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4),
            2,
        )
        pygame.draw.circle(self.screen, color, (cx, cy), TowerClass.DATA["range"], 1)

    def _draw_hud(self):
        y = 6
        entries = [
            (f"Score: {self.score}", COLOR_TEXT),
            (f"Lives: {self.lives}", COLOR_TEXT),
            (f"Gold: {self.gold}", COLOR_GOLD),
            (f"Wave: {self.wave_number}/{len(WAVES)}", COLOR_TEXT),
        ]

        for text, color in entries:
            surf = self.font.render(text, True, color)
            self.screen.blit(surf, (8, y))
            y += 22

        if self.store.selected_tower_class:
            name = self.store.selected_tower_class.DATA["name"]
            placing = self.font.render(f"Placing: {name}", True, (180, 220, 255))
            self.screen.blit(placing, (8, y + 4))
            y += 26

        if self.selected_map_tower:
            tower = self.selected_map_tower
            lines = [
                f"Selected: {tower.name} L{tower.level}",
                f"Upgrade: U ({tower.get_upgrade_cost()}g)" if tower.can_upgrade() else "Upgrade: MAX",
                f"Sell: S ({tower.get_sell_value()}g)",
            ]
            for line in lines:
                surf = self.font.render(line, True, COLOR_TEXT)
                self.screen.blit(surf, (8, y + 4))
                y += 22

        if self.state == "intermission":
            if self.wave_number < len(WAVES):
                msg = "Press SPACE to start next wave"
                surf = self.big_font.render(msg, True, COLOR_TEXT)
                self.screen.blit(surf, (130, 20))
        elif self.state == "game_over":
            surf = self.big_font.render("GAME OVER", True, (255, 100, 100))
            self.screen.blit(surf, (240, 20))
        elif self.state == "victory":
            surf = self.big_font.render("VICTORY!", True, (120, 255, 120))
            self.screen.blit(surf, (260, 20))

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


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()