import math
import pygame

from constants import (
    CELL_SIZE,
    PROJECTILE_SPEED,
    PROJECTILE_SIZE,
    COLOR_PROJECTILE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SELL_REFUND_RATIO,
)


class Projectile:
    """
    Projectile fired by a tower toward a target enemy.

    Supports optional special hit effects through `on_hit`, which allows
    towers like SlowTower or SplashTower to customize what happens on impact.
    """

    def __init__(
        self,
        x,
        y,
        target_enemy,
        damage,
        speed=PROJECTILE_SPEED,
        size=PROJECTILE_SIZE,
        color=COLOR_PROJECTILE,
        enemies=None,
        on_hit=None,
    ):
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.size = size
        self.color = color
        self.active = True
        self.target = target_enemy
        self.enemies = enemies if enemies is not None else []
        self.on_hit = on_hit
        self.speed = speed

        dx = target_enemy.x - x
        dy = target_enemy.y - y
        dist = math.hypot(dx, dy) or 1
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed

    def update(self):
        if not self.active:
            return

        if not self.target.alive:
            self.active = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        enemy_hit_radius = self.target.size / 2
        projectile_hit_radius = self.size / 2

        if dist <= enemy_hit_radius + projectile_hit_radius:
            self.target.take_damage(self.damage)
            if self.on_hit:
                self.on_hit(self.target, self.enemies)
            self.active = False
            return

        if dist != 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed

        self.x += self.vx
        self.y += self.vy

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist <= enemy_hit_radius + projectile_hit_radius:
            self.target.take_damage(self.damage)
            if self.on_hit:
                self.on_hit(self.target, self.enemies)
            self.active = False
            return

        if not (0 <= self.x <= SCREEN_WIDTH and 0 <= self.y <= SCREEN_HEIGHT):
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        pygame.draw.circle(
            surface,
            self.color,
            (int(self.x), int(self.y)),
            self.size // 2,
        )


class BaseTower:
    """
    Base tower class.

    Towers are placed on a grid cell and fire projectiles at enemies within range.
    Subclasses define their stats using the DATA dictionary and can override
    targeting or projectile behavior.
    """

    DATA = {}

    def __init__(self, col, row):
        self.col = col
        self.row = row
        self.x = col * CELL_SIZE + CELL_SIZE // 2
        self.y = row * CELL_SIZE + CELL_SIZE // 2

        d = self.__class__.DATA
        self.name = d["name"]
        self.color = d["color"]
        self.range = d["range"]
        self.damage = d["damage"]
        self.fire_rate = d["fire_rate"]
        self.proj_speed = d["proj_speed"]
        self.proj_size = d["proj_size"]
        self.proj_color = d["proj_color"]
        self.cost = d["cost"]

        self.fire_timer = 0
        self.level = 1
        self.total_spent = self.cost

    def update(self, enemies, projectiles):
        if self.fire_timer > 0:
            self.fire_timer -= 1
            return

        target = self._get_target(enemies)
        if target:
            proj = self._make_projectile(target, enemies)
            projectiles.append(proj)
            self._on_fire(target, projectiles)
            self.fire_timer = self.fire_rate

    def _make_projectile(self, target, enemies):
        return Projectile(
            self.x,
            self.y,
            target,
            self.damage,
            speed=self.proj_speed,
            size=self.proj_size,
            color=self.proj_color,
            enemies=enemies,
        )

    def _get_target(self, enemies):
        """
        Default targeting: choose the closest enemy within range.
        """
        closest = None
        closest_dist = self.range

        for enemy in enemies:
            if not enemy.alive:
                continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy

        return closest

    def _on_fire(self, target, projectiles):
        """
        Hook for subclasses to add special behavior when firing.
        """
        pass

    def can_upgrade(self):
        return self.level < 3

    def get_upgrade_cost(self):
        return 25 * self.level

    def upgrade(self):
        upgrade_cost = self.get_upgrade_cost()
        self.total_spent += upgrade_cost
        self.level += 1
        self.damage = int(self.damage * 1.5)
        self.range += 25
        self.fire_rate = max(8, int(self.fire_rate * 0.8))

    def get_sell_value(self):
        return int(self.total_spent * SELL_REFUND_RATIO)

    def draw(self, surface):
        size = CELL_SIZE - 4
        half = size // 2
        rect = pygame.Rect(self.x - half, self.y - half, size, size)
        pygame.draw.rect(surface, self.color, rect)

        font = pygame.font.SysFont(None, 20)
        label = font.render(self.name[0], True, (255, 255, 255))
        lx = self.x - label.get_width() // 2
        ly = self.y - label.get_height() // 2
        surface.blit(label, (lx, ly))


class BasicTower(BaseTower):
    """
    Balanced beginner tower.
    """
    DATA = {
        "name": "Basic",
        "description": "Balanced range, damage & speed.",
        "cost": 50,
        "color": (60, 120, 200),
        "range": 120,
        "damage": 26,
        "fire_rate": 45,
        "proj_speed": 5,
        "proj_size": 8,
        "proj_color": (255, 230, 50),
    }


class SniperTower(BaseTower):
    """
    Long-range tower that prefers enemies furthest along the path.
    """
    DATA = {
        "name": "Sniper",
        "description": "Long range, high damage, slow fire.",
        "cost": 120,
        "color": (180, 60, 180),
        "range": 240,
        "damage": 60,
        "fire_rate": 120,
        "proj_speed": 9,
        "proj_size": 6,
        "proj_color": (220, 120, 255),
    }

    def _get_target(self, enemies):
        in_range = [
            e for e in enemies
            if e.alive and math.hypot(e.x - self.x, e.y - self.y) <= self.range
        ]
        if not in_range:
            return None
        return max(in_range, key=lambda e: e.waypoint_index)


class RapidTower(BaseTower):
    """
    Fast-firing tower with short range and low damage per shot.
    """
    DATA = {
        "name": "Rapid",
        "description": "Short range, fast fire rate.",
        "cost": 80,
        "color": (60, 200, 120),
        "range": 100,
        "damage": 11,
        "fire_rate": 15,
        "proj_speed": 7,
        "proj_size": 5,
        "proj_color": (150, 255, 180),
    }


class SlowTower(BaseTower):
    """
    Support tower that slows enemies on hit.
    """
    DATA = {
        "name": "Slow",
        "description": "Applies a slow debuff.",
        "cost": 90,
        "color": (80, 180, 255),
        "range": 110,
        "damage": 10,
        "fire_rate": 45,
        "proj_speed": 5,
        "proj_size": 7,
        "proj_color": (120, 220, 255),
    }

    def _make_projectile(self, target, enemies):
        def apply_slow(enemy, _enemy_list):
            enemy.apply_slow(0.5, 90)

        return Projectile(
            self.x,
            self.y,
            target,
            self.damage,
            speed=self.proj_speed,
            size=self.proj_size,
            color=self.proj_color,
            enemies=enemies,
            on_hit=apply_slow,
        )


class SplashTower(BaseTower):
    """
    Area-damage tower. On hit, damages nearby enemies as well.
    """
    DATA = {
        "name": "Splash",
        "description": "Deals area damage on hit.",
        "cost": 140,
        "color": (255, 140, 60),
        "range": 130,
        "damage": 26,
        "fire_rate": 75,
        "proj_speed": 6,
        "proj_size": 8,
        "proj_color": (255, 180, 90),
    }

    def _make_projectile(self, target, enemies):
        def splash(enemy, enemy_list):
            for other in enemy_list:
                if other.alive and math.hypot(other.x - enemy.x, other.y - enemy.y) <= 45:
                    other.take_damage(12)

        return Projectile(
            self.x,
            self.y,
            target,
            self.damage,
            speed=self.proj_speed,
            size=self.proj_size,
            color=self.proj_color,
            enemies=enemies,
            on_hit=splash,
        )