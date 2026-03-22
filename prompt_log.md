# This entire file contains the work done on the project by the person who did Phase 1. I have made no edits it since then. My prompt log is in the README.md

# AI PROMPTS:
I talked with Claude for this project so far.

### ME: 
I want to create a python tower defense game. Please only create the boilerplate with only basic pygame boxes to add to later. Please add comments to explain everything written.

### CLAUDE:
I'll dive straight into writing the boilerplate Python pygame tower defense game.Here's the boilerplate — run it with `pip install pygame` then `python tower_defense.py`.

**What's included:**

- **`Enemy`** — walks along a grid path defined by waypoints, has health and a health bar drawn above it
- **`Tower`** — placed by left-clicking any non-path cell, scans for the nearest enemy in range and fires
- **`Projectile`** — travels in a straight line toward the enemy position at the moment of firing
- **`Game`** — owns all state, runs the main loop (handle input → update → draw)

**Everything is just colored boxes** — no sprites or images, as requested — so it's easy to layer on visuals later.

**Natural next steps to build on this:**
- Replace `pygame.draw.rect` calls with sprite images
- Add multiple tower types (different ranges/damage/fire rates)
- Expand `WAYPOINTS` for a more complex map
- Wire up waves (spawn in bursts rather than a steady stream)
- Add a UI panel for selecting which tower to buy and a gold/currency system
- Add a game-over screen when `lives` hits 0

### ME:
ok perfect. I now want to create a store to buy different kinds of towers and costing different each. Can we separate files so that different tower classes are in their own file and then called in this main file? Please do three different classes for now, also making it clear the best way to add new classes.

### CLAUDE:
Let me read the existing file first, then build out the multi-file structure.Good, I have the full picture. Now I'll create all four files: `constants.py`, `towers.py`, `store.py`, and the rewritten `tower_defense.py`.Here's the full breakdown of the four files. Keep them all in the same folder and run with `python tower_defense.py`.

---

**File structure:**

```
constants.py       ← all numbers, colors, path data (single source of truth)
towers.py          ← BaseTower + 3 tower subclasses + Projectile
store.py           ← store panel UI, card rendering, selection logic
tower_defense.py   ← Game class + main loop (imports from all three above)
```

---

**The three towers:**

| Tower | Cost | Range | Damage | Fire Rate | Strategy |
|---|---|---|---|---|---|
| **Basic** | 50g | 120px | 20 | 1/sec | All-rounder, buy early |
| **Sniper** | 120g | 240px | 60 | 0.5/sec | Targets furthest-along enemy |
| **Rapid** | 80g | 80px | 8 | 4/sec | Shreds enemies at close range |

---

**To add a new tower — only 2 steps:**

1. In `towers.py`, copy the template at the bottom and fill in your `DATA` dict. Optionally override `_get_target()`, `_on_fire()`, or `draw()`.
2. In `store.py`, import your class and append it to `TOWER_CATALOG`. A new card appears automatically.

That's it — `tower_defense.py` never needs to be touched.
