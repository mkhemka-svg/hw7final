# Tower Defense

So far this game is a very basic tower defense. It features:
- a grid system for towers
- a short path for enemies
- one enemy type
- three tower types
- a store

What it is missing is up to you, by most notably, this game is impossible to win.
Consider adding:
- new enemies
- new towers
- moving/selling towers
- levels
- graphics
- etc.

To run:
```bash
pip install pygame
python3 tower_defense.py
```

The files are:
| File | Description |
|---|---|
| tower_defense.py | the main housing of the game logic |
| constants.py | the constants, including "waypoints" to describe the map the enemies follow |
| towers.py | the different tower types. Please check the prompt_log for descriptions of existing and check the file for how to add new ones |
| store.py | store logic for towers |

Comments are in every file to explain. Check the prompt_log.md for some more info!