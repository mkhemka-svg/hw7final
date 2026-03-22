# Tower Defense Game (Phase 2)

## Overview
For Phase 2, I worked on a Python-based Tower Defense game built using Pygame. The original project was a functional prototype with core mechanics implemented, but it lacked progression structure, strategic depth, and polish.

My goal in this phase was to transform the game from a basic demo into a more complete and playable tower defense experience with improved balance, user interaction, and game flow.

---

## Initial Project State
The project initially included:
- Basic grid-based map with a fixed enemy path
- A single enemy type with constant spawning (no waves)
- Three tower types (Basic, Sniper, Rapid) with simple targeting
- Projectile system with straight-line motion
- Basic store UI for placing towers
- No win condition (game was endless and unwinnable)
- No upgrade, sell, or restart mechanics

Limitations:
- No structured progression (no waves)
- Limited strategy (no enemy diversity or tower specialization)
- Poor game balance (too difficult early on)
- No game-over or victory states
- Projectile accuracy issues (missed moving enemies)

---

## Changes Implemented

### 1. Wave System & Game Flow
- Replaced continuous spawning with structured waves
- Implemented:
  - `WAVES` system in `constants.py`
  - Intermission phase between waves
  - Victory condition after final wave
  - Game-over condition when lives reach 0

### 2. Enemy Variety
Added multiple enemy types:
- BasicEnemy (standard)
- FastEnemy (high speed, low health)
- ArmoredEnemy (high health, damage reduction)
- BossEnemy (high difficulty, high reward)

This increased strategic complexity and required varied tower usage.

---

### 3. Tower System Enhancements
Expanded tower mechanics:
- Added **SlowTower** (applies movement debuff)
- Added **SplashTower** (area damage)
- Introduced upgrade system:
  - Level-based stat scaling (damage, range, fire rate)
- Added selling system:
  - Refund based on total investment

---

### 4. Projectile System Fix (Major Bug Fix)
- Original issue: projectiles missed moving enemies
- Implemented **homing behavior**:
  - Projectiles now track enemies every frame
- Fixed collision detection using radius-based hit logic:
  - Matches visual overlap with actual hit detection

---

### 5. Economy & Balance Improvements
Adjusted game balance to improve playability:
- Increased starting gold and lives
- Increased enemy rewards
- Reduced upgrade costs
- Slowed enemy spawn rate
- Reworked early waves to be less punishing

---

### 6. UI & Interaction Improvements
- Added tower selection system (click to select towers)
- Added:
  - Upgrade (`U`) and Sell (`S`) controls
  - Range preview before placement
  - Tower info display (level, cost, stats)
- Improved HUD with:
  - Wave tracking
  - Gold, lives, score display

---

### 7. Restart Functionality
- Added ability to restart game using `R`
- Fully resets:
  - towers, enemies, gold, lives, waves, UI state

---

## Challenges Encountered

### 1. Projectile Accuracy Bug
**Problem:** Projectiles visually hit enemies but did not register damage  
**Cause:** Collision detection was too strict and based on outdated position logic  
**Solution:**
- Implemented radius-based collision detection
- Added homing projectile logic (recalculating direction every frame)

---

### 2. Game Balance
**Problem:** Game was too difficult early and unwinnable  
**Solution:**
- Reworked wave structure
- Increased rewards and starting resources
- Buffed early-game towers

---

### 3. State Management Complexity
**Problem:** Managing transitions between:
- Intermission
- Playing
- Victory
- Game Over

**Solution:**
- Introduced `self.state` system
- Cleanly separated logic for each phase

---

### 4. Code Integration Across Files
The project spans multiple modules:
- `tower_defense.py`
- `towers.py`
- `store.py`
- `constants.py`
- `enemies.py`

Ensuring compatibility across:
- enemy logic
- projectile behavior
- UI interactions  
was a key challenge.

---

## Prompt Log (AI Usage)

### Tools Used
- ChatGPT 

---

### Key Prompts

#### 1. System Expansion
> "Using all the information in these files, suggest changes to create a full tower defense game"

Helped define:
- waves
- enemy types
- upgrades
- UI improvements

---

#### 2. Step-by-Step Implementation
> "Tell me exactly the code to change or write step by step"

Used to:
- implement wave system
- add enemies
- integrate UI logic

---

#### 3. Code Refactoring
> "Create a compiled version of what the new towers.py should look like"

Used to:
- consolidate all tower logic
- add Slow and Splash towers
- implement upgrade/sell systems

---

#### 4. Debugging Projectile Issues
> "Projectiles are not hitting enemies accurately"

and

> "Even when it hits visually, enemy health is not going down"

Led to:
- switching to homing projectiles
- fixing collision detection using radius-based checks

---

#### 5. Game Balancing
> "Make the game more winnable for players"

Helped adjust:
- wave difficulty
- rewards
- tower stats
- upgrade costs

---

#### 6. Restart Feature
> "Implement an option so that you can restart the game"

Used to:
- add reset_game()
- bind restart key
- update UI

---

## Final Result
The final game is now:
- Fully playable from start to finish
- Winnable with strategic play
- Balanced for a smooth difficulty curve
- Rich in mechanics (enemy types, tower types, upgrades)
- More interactive and user-friendly

---

## Controls

- Left Click → Place tower / Select tower
- Right Click → Deselect
- U → Upgrade selected tower
- S → Sell selected tower
- SPACE → Start next wave
- R → Restart game
- ESC → Quit

---

## Future Improvements (Optional)
- Sprite-based visuals instead of rectangles
- Sound effects (shooting, hits, wave start)
- Multiple maps
- Advanced targeting modes (first, last, strongest)
- Boss abilities or special mechanics

---
