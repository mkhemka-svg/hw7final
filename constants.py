"""
constants.py
============
All shared constants for the tower defense game.
"""

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# ---------------------------------------------------------------------------
# Store panel
# ---------------------------------------------------------------------------
STORE_WIDTH = 180
MAP_WIDTH = SCREEN_WIDTH - STORE_WIDTH

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
CELL_SIZE = 40
GRID_COLS = MAP_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
COLOR_BG = (30, 30, 30)
COLOR_GRID = (50, 50, 50)
COLOR_PATH = (180, 140, 80)
COLOR_ENEMY = (220, 60, 60)
COLOR_PROJECTILE = (255, 230, 50)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_DIM = (150, 150, 150)

COLOR_STORE_BG = (20, 20, 40)
COLOR_STORE_BORDER = (80, 80, 120)
COLOR_CARD_BG = (35, 35, 60)
COLOR_CARD_HOVER = (55, 55, 90)
COLOR_CARD_SEL = (70, 70, 130)
COLOR_GOLD = (255, 210, 50)

# ---------------------------------------------------------------------------
# Enemy base stats
# ---------------------------------------------------------------------------
ENEMY_SPEED = 2
ENEMY_HEALTH = 100
ENEMY_SIZE = 20
ENEMY_SPAWN_RATE = 45   # frames between spawns inside a wave

# ---------------------------------------------------------------------------
# Projectile
# ---------------------------------------------------------------------------
PROJECTILE_SPEED = 5
PROJECTILE_SIZE = 8

# ---------------------------------------------------------------------------
# Path waypoints
# ---------------------------------------------------------------------------
WAYPOINTS = [
    (0, 3),
    (5, 3),
    (5, 10),
    (12, 10),
    (12, 5),
    (17, 5),
]

def waypoint_to_pixel(col, row):
    return (
        col * CELL_SIZE + CELL_SIZE // 2,
        row * CELL_SIZE + CELL_SIZE // 2,
    )

WAYPOINT_PIXELS = [waypoint_to_pixel(c, r) for c, r in WAYPOINTS]

def build_path_cells():
    cells = set()
    for i in range(len(WAYPOINTS) - 1):
        c0, r0 = WAYPOINTS[i]
        c1, r1 = WAYPOINTS[i + 1]

        dc = (1 if c1 > c0 else -1) if c1 != c0 else 0
        dr = (1 if r1 > r0 else -1) if r1 != r0 else 0

        c, r = c0, r0
        while (c, r) != (c1, r1):
            cells.add((c, r))
            c += dc
            r += dr
        cells.add((c1, r1))
    return cells

PATH_CELLS = build_path_cells()

# ---------------------------------------------------------------------------
# Economy / progression
# ---------------------------------------------------------------------------
STARTING_GOLD = 400
STARTING_LIVES = 30
SELL_REFUND_RATIO = 0.7
TIME_BETWEEN_WAVES = 240

ENEMY_REWARDS = {
    "basic": 15,
    "fast": 18,
    "armored": 25,
    "boss": 150,
}

WAVES = [
    [("basic", 4)],
    [("basic", 5)],
    [("basic", 6), ("fast", 1)],
    [("basic", 7), ("fast", 2)],
    [("basic", 6), ("armored", 2)],
    [("fast", 4), ("armored", 2)],
    [("boss", 1), ("basic", 4)],
]