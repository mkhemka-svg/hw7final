"""
towers.py
=========
Contains the BaseTower class and every concrete tower subclass.

HOW TO ADD A NEW TOWER
----------------------
1. Create a new class that inherits from BaseTower (see the template at
   the bottom of this file).
2. Override the class-level DATA dictionary with your tower's unique stats.
3. Optionally override `draw()` if you want a different visual shape.
4. Optionally override `_get_target()` if you want a different targeting
   strategy (e.g. "target the enemy with the most health").
5. Register the new class in towers/store.py → TOWER_CATALOG list so it
   appears in the in-game store.

That's it — no changes needed anywhere else.

Current tower roster
--------------------
  BasicTower   – affordable all-rounder
  SniperTower  – long range, slow fire rate, high damage
  RapidTower   – short range, very fast fire rate, low damage per shot
"""

import pygame
import math

from constants import (
    CELL_SIZE,
    PROJECTILE_SPEED,
    PROJECTILE_SIZE,
    COLOR_PROJECTILE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)


# ===========================================================================
# Projectile
# ===========================================================================
# Kept in this file because it is tightly coupled to towers.
# Each tower creates Projectile instances; the Game class stores and updates
# them.

class Projectile:
    """
    A projectile fired by a tower.

    Travels in a straight line toward the enemy's position at the moment of
    firing (not homing).  Deactivates on hit, on miss, or when off-screen.
    """

    def __init__(self, x, y, target_enemy, damage,
                 speed=PROJECTILE_SPEED,
                 size=PROJECTILE_SIZE,
                 color=COLOR_PROJECTILE):
        self.x      = float(x)
        self.y      = float(y)
        self.damage = damage
        self.size   = size
        self.color  = color
        self.active = True
        self.target = target_enemy  # keep a reference to check collision

        # Direction toward target at the moment of firing
        dx = target_enemy.x - x
        dy = target_enemy.y - y
        dist = math.hypot(dx, dy) or 1
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed

    def update(self):
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy

        if self.target.alive:
            dist = math.hypot(self.target.x - self.x, self.target.y - self.y)
            if dist < abs(self.vx) + self.size:   # close enough → hit
                self.target.take_damage(self.damage)
                self.active = False
        else:
            self.active = False  # target already dead

        # Off-screen check
        if not (0 <= self.x <= SCREEN_WIDTH and 0 <= self.y <= SCREEN_HEIGHT):
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        half = self.size // 2
        pygame.draw.rect(surface, self.color,
                         pygame.Rect(self.x - half, self.y - half,
                                     self.size, self.size))


# ===========================================================================
# BaseTower
# ===========================================================================

class BaseTower:
    """
    Abstract base class for all towers.

    Subclasses MUST define a DATA dict with these keys:
        name        str   – display name shown in the store
        description str   – one-line tooltip shown in the store
        cost        int   – gold price
        color       tuple – (R,G,B) box color
        range       int   – detection radius in pixels
        damage      int   – hit points removed per projectile
        fire_rate   int   – frames between shots (higher = slower)
        proj_speed  int   – pixels per frame for this tower's projectiles
        proj_size   int   – projectile box size in pixels
        proj_color  tuple – (R,G,B) projectile color

    Subclasses MAY override:
        draw(surface)           – custom visual (default: filled box + label)
        _get_target(enemies)    – targeting strategy (default: nearest enemy)
        _on_fire(target, proj_list) – called after a projectile is spawned
                                      (useful for multi-shot or splash towers)
    """

    # Subclasses override this dict; BaseTower itself is never instantiated.
    DATA = {}

    def __init__(self, col, row):
        self.col = col
        self.row = row
        # Pixel centre of this grid cell
        self.x = col * CELL_SIZE + CELL_SIZE // 2
        self.y = row * CELL_SIZE + CELL_SIZE // 2

        # Pull stats from the class-level DATA dict
        d = self.__class__.DATA
        self.name       = d["name"]
        self.color      = d["color"]
        self.range      = d["range"]
        self.damage     = d["damage"]
        self.fire_rate  = d["fire_rate"]
        self.proj_speed = d["proj_speed"]
        self.proj_size  = d["proj_size"]
        self.proj_color = d["proj_color"]

        self.fire_timer = 0   # counts down frames until next shot is allowed

    # ------------------------------------------------------------------
    # Update (called every frame by the Game)
    # ------------------------------------------------------------------

    def update(self, enemies, projectiles):
        """Tick the cooldown timer; fire when ready and a target exists."""
        if self.fire_timer > 0:
            self.fire_timer -= 1
            return

        target = self._get_target(enemies)
        if target:
            proj = Projectile(
                self.x, self.y, target,
                self.damage,
                speed=self.proj_speed,
                size=self.proj_size,
                color=self.proj_color,
            )
            projectiles.append(proj)
            self._on_fire(target, projectiles)   # hook for special behavior
            self.fire_timer = self.fire_rate

    # ------------------------------------------------------------------
    # Targeting strategy  (override for different behavior)
    # ------------------------------------------------------------------

    def _get_target(self, enemies):
        """Return the nearest alive enemy within self.range, or None."""
        closest, closest_dist = None, self.range
        for enemy in enemies:
            if not enemy.alive:
                continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy
        return closest

    # ------------------------------------------------------------------
    # Post-fire hook  (override for multi-shot, splash, etc.)
    # ------------------------------------------------------------------

    def _on_fire(self, target, projectiles):
        """Called immediately after the main projectile is created.
        Override to add extra projectiles, apply status effects, etc."""
        pass  # default: do nothing extra

    # ------------------------------------------------------------------
    # Drawing  (override for custom visuals)
    # ------------------------------------------------------------------

    def draw(self, surface):
        """Draw a filled box with a one-letter label.  Override for sprites."""
        size = CELL_SIZE - 4
        half = size // 2
        rect = pygame.Rect(self.x - half, self.y - half, size, size)
        pygame.draw.rect(surface, self.color, rect)

        # Small label so the player can tell towers apart at a glance
        font = pygame.font.SysFont(None, 20)
        label = font.render(self.name[0], True, (255, 255, 255))
        lx = self.x - label.get_width()  // 2
        ly = self.y - label.get_height() // 2
        surface.blit(label, (lx, ly))


# ===========================================================================
# Concrete tower classes
# ===========================================================================

class BasicTower(BaseTower):
    """
    BasicTower — the starter tower.

    Balanced range, damage, and fire rate.  Cheap enough to buy early.
    Good all-rounder; place several of these to cover a long stretch of path.
    """
    DATA = {
        "name":        "Basic",
        "description": "Balanced range, damage & speed.",
        "cost":        50,
        "color":       (60, 120, 200),   # blue
        "range":       120,
        "damage":      20,
        "fire_rate":   60,               # 1 shot/sec at 60 FPS
        "proj_speed":  5,
        "proj_size":   8,
        "proj_color":  (255, 230, 50),   # yellow
    }
    # No overrides needed — default behavior is fine.


class SniperTower(BaseTower):
    """
    SniperTower — long-range, high-damage, slow-firing.

    Fires once every ~2 seconds but hits hard and can reach enemies that
    other towers can't.  Best placed near the start or end of the path
    where enemies spend the most time.
    """
    DATA = {
        "name":        "Sniper",
        "description": "Long range, high damage, slow fire.",
        "cost":        120,
        "color":       (180, 60, 180),   # purple
        "range":       240,              # 2× the basic range
        "damage":      60,               # 3× the basic damage
        "fire_rate":   120,              # 1 shot every 2 seconds
        "proj_speed":  9,                # fast projectile
        "proj_size":   6,
        "proj_color":  (220, 120, 255),  # light purple
    }

    def _get_target(self, enemies):
        """
        Sniper targets the enemy that has progressed the furthest along the
        path (highest waypoint_index), rather than simply the nearest.
        Override example: swap the key function to change priority.
        """
        in_range = [
            e for e in enemies
            if e.alive and math.hypot(e.x - self.x, e.y - self.y) <= self.range
        ]
        if not in_range:
            return None
        # Pick the enemy closest to the end of the path
        return max(in_range, key=lambda e: e.waypoint_index)


class RapidTower(BaseTower):
    """
    RapidTower — short-range, low-damage, very fast fire rate.

    Fires ~4 times per second.  Low individual damage but can overwhelm
    weakened or slow enemies.  Best placed at a curve where enemies slow
    down (conceptually) and spend more frames in range.
    """
    DATA = {
        "name":        "Rapid",
        "description": "Short range, fast fire rate.",
        "cost":        80,
        "color":       (60, 200, 120),   # green
        "range":       80,               # shorter range than Basic
        "damage":      8,                # low damage per shot
        "fire_rate":   15,               # ~4 shots/sec
        "proj_speed":  7,
        "proj_size":   5,
        "proj_color":  (150, 255, 180),  # light green
    }
    # Uses default nearest-enemy targeting and no post-fire hook.


# ===========================================================================
# ── HOW TO ADD A NEW TOWER ─────────────────────────────────────────────────
#
# Copy this template, fill in your values, and add the class name to
# TOWER_CATALOG in store.py.  Nothing else needs to change.
#
# class MyNewTower(BaseTower):
#     """
#     One-line summary of what makes this tower special.
#     """
#     DATA = {
#         "name":        "MyNew",           # short name (first letter = box label)
#         "description": "What it does.",   # shown in the store card
#         "cost":        ???,               # gold cost
#         "color":       (R, G, B),         # box color on the map
#         "range":       ???,               # detection radius in pixels
#         "damage":      ???,               # damage per projectile
#         "fire_rate":   ???,               # frames between shots
#         "proj_speed":  ???,               # projectile pixels per frame
#         "proj_size":   ???,               # projectile box size (px)
#         "proj_color":  (R, G, B),         # projectile color
#     }
#
#     # Optional overrides:
#
#     def _get_target(self, enemies):
#         # Custom targeting logic here.
#         # Return one Enemy object or None.
#         return super()._get_target(enemies)   # or your own logic
#
#     def _on_fire(self, target, projectiles):
#         # Called after the first projectile is added.
#         # Append extra Projectile objects here for multi-shot towers.
#         pass
#
#     def draw(self, surface):
#         # Custom drawing here (circle, triangle, sprite, etc.)
#         super().draw(surface)   # or replace entirely
#
# ===========================================================================