"""
constants.py
============
All shared constants for the tower defense game.

Every other module imports from here so there is a single source of truth.
If you need to tweak a value (e.g. screen size, grid cell size, colors),
change it here and it will be reflected everywhere automatically.
"""

# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
SCREEN_WIDTH  = 900   # extra width (vs old 800) to make room for the store panel
SCREEN_HEIGHT = 600
FPS           = 60

# ---------------------------------------------------------------------------
# Store panel
# ---------------------------------------------------------------------------
# The right-hand side of the window is reserved for the tower store.
# The playable map occupies the remaining left portion.
STORE_WIDTH  = 180                        # pixels wide
MAP_WIDTH    = SCREEN_WIDTH - STORE_WIDTH # 720 px — the grid lives here

# ---------------------------------------------------------------------------
# Grid
# ---------------------------------------------------------------------------
CELL_SIZE  = 40
GRID_COLS  = MAP_WIDTH    // CELL_SIZE   # 18 columns
GRID_ROWS  = SCREEN_HEIGHT // CELL_SIZE  # 15 rows

# ---------------------------------------------------------------------------
# Colors  (R, G, B)
# ---------------------------------------------------------------------------
COLOR_BG          = (30,  30,  30)
COLOR_GRID        = (50,  50,  50)
COLOR_PATH        = (180, 140,  80)
COLOR_ENEMY       = (220,  60,  60)
COLOR_PROJECTILE  = (255, 230,  50)
COLOR_TEXT        = (230, 230, 230)
COLOR_TEXT_DIM    = (150, 150, 150)

# Store panel colors
COLOR_STORE_BG    = (20,  20,  40)   # dark navy background for the store
COLOR_STORE_BORDER= (80,  80, 120)   # border between map and store
COLOR_CARD_BG     = (35,  35,  60)   # individual tower card background
COLOR_CARD_HOVER  = (55,  55,  90)   # card background when mouse hovers
COLOR_CARD_SEL    = (70,  70, 130)   # card background when selected
COLOR_GOLD        = (255, 210,  50)  # gold / currency text

# ---------------------------------------------------------------------------
# Enemy
# ---------------------------------------------------------------------------
ENEMY_SPEED      = 2
ENEMY_HEALTH     = 100
ENEMY_SIZE       = 20
ENEMY_SPAWN_RATE = 120   # frames between spawns

# ---------------------------------------------------------------------------
# Projectile
# ---------------------------------------------------------------------------
PROJECTILE_SPEED = 5
PROJECTILE_SIZE  = 8

# ---------------------------------------------------------------------------
# Path waypoints  (col, row) — enemies follow these across the grid
# ---------------------------------------------------------------------------
# Extend this list to create a more complex map layout.
WAYPOINTS = [
    (0,  3),
    (5,  3),
    (5,  10),
    (12, 10),
    (12, 5),
    (17, 5),   # exit at right edge of MAP_WIDTH (col 17 = last column)
]

def waypoint_to_pixel(col, row):
    """Convert grid (col, row) to pixel centre of that cell."""
    return (col * CELL_SIZE + CELL_SIZE // 2,
            row * CELL_SIZE + CELL_SIZE // 2)

WAYPOINT_PIXELS = [waypoint_to_pixel(c, r) for c, r in WAYPOINTS]

def build_path_cells():
    """Return a set of (col, row) cells that form the enemy path."""
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
# Starting gold
# ---------------------------------------------------------------------------
STARTING_GOLD = 200