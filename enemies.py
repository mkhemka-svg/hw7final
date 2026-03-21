import math
import pygame

from constants import (
    WAYPOINT_PIXELS,
    COLOR_ENEMY,
    ENEMY_SPEED,
    ENEMY_HEALTH,
    ENEMY_SIZE,
    ENEMY_REWARDS,
)


class BaseEnemy:
    COLOR = COLOR_ENEMY
    NAME = "basic"
    MAX_HEALTH = ENEMY_HEALTH
    SPEED = ENEMY_SPEED
    SIZE = ENEMY_SIZE

    def __init__(self):
        self.x, self.y = WAYPOINT_PIXELS[0]
        self.health = self.MAX_HEALTH
        self.max_health = self.MAX_HEALTH
        self.base_speed = self.SPEED
        self.size = self.SIZE
        self.reward = ENEMY_REWARDS[self.NAME]

        self.alive = True
        self.reached_end = False
        self.waypoint_index = 1

        # status effects
        self.slow_timer = 0
        self.slow_factor = 1.0

    def apply_slow(self, factor, duration):
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def update(self):
        if not self.alive or self.reached_end:
            return

        if self.slow_timer > 0:
            self.slow_timer -= 1
            current_speed = self.base_speed * self.slow_factor
        else:
            self.slow_factor = 1.0
            current_speed = self.base_speed

        tx, ty = WAYPOINT_PIXELS[self.waypoint_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        if dist <= current_speed:
            self.x, self.y = tx, ty
            self.waypoint_index += 1
            if self.waypoint_index >= len(WAYPOINT_PIXELS):
                self.reached_end = True
        else:
            self.x += (dx / dist) * current_speed
            self.y += (dy / dist) * current_speed

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return

        half = self.size // 2
        pygame.draw.rect(
            surface,
            self.COLOR,
            pygame.Rect(self.x - half, self.y - half, self.size, self.size),
        )

        # health bar
        bw, bh = self.size, 4
        bx, by = self.x - half, self.y - half - 6
        ratio = max(0, self.health / self.max_health)

        pygame.draw.rect(surface, (80, 0, 0), pygame.Rect(bx, by, bw, bh))
        pygame.draw.rect(surface, (0, 200, 80), pygame.Rect(bx, by, int(bw * ratio), bh))


class BasicEnemy(BaseEnemy):
    NAME = "basic"
    COLOR = (220, 60, 60)


class FastEnemy(BaseEnemy):
    NAME = "fast"
    MAX_HEALTH = 70
    SPEED = 3.2
    SIZE = 16
    COLOR = (255, 180, 60)


class ArmoredEnemy(BaseEnemy):
    NAME = "armored"
    MAX_HEALTH = 220
    SPEED = 1.4
    SIZE = 24
    COLOR = (120, 150, 220)

    def take_damage(self, amount):
        reduced = max(1, int(amount * 0.7))
        super().take_damage(reduced)


class BossEnemy(BaseEnemy):
    NAME = "boss"
    MAX_HEALTH = 600
    SPEED = 1.2
    SIZE = 30
    COLOR = (180, 80, 220)