# Reencor
 
A retro-inspired 2D fighting game featuring classic-style sprites, Pygame, and OpenGL.

## Demo

https://github.com/user-attachments/assets/1bc77764-fea2-4dc3-a70f-b5bfc6aef54b

## Version

**Version:** 0.4.1-alpha

## Features

- Classic 2D fighting mechanics
- Keyboard and controller support
- OpenGL rendering

## Requirements

- Python 3.14.0
- [Pygame](https://www.pygame.org/) (standard version)
- pygame._sdl2 (included in standard Pygame, required for controller support)
- [PyOpenGL](http://pyopengl.sourceforge.net/)
- [moderngl](https://moderngl.readthedocs.io/)
- [PyGLM](https://pypi.org/project/PyGLM/)
- [NumPy](https://numpy.org/)
- [Pillow (PIL)](https://pillow.readthedocs.io/)

- **Not compatible with pygame-ce**

## Sprites

This game uses character sprites from *Street Fighter III* for educational purposes only.

You can download the sprites from the following source:

- [Ryu Street Fighter III (Sprite Sets)](https://www.nowak.ca/zweifuss/all/02_Ryu.zip)
- [Ingame effects Street Fighter III (Sprite Sets)](https://www.justnopoint.com/zweifuss/all/22_Ingame%20Effects.zip)

Unzip the file and place the folder in the `Assets/images` folder before running the game.

## Basic Controls

| Action              | Input                    |
|---------------------|--------------------------|
| Move Left           | ←                        |
| Move Right          | →                        |
| Crouch              | ↓                        |
| Jump                | ↑                        |
| Light Punch (LP)    | A                        |
| Medium Punch (MP)   | S                        |
| Heavy Punch (HP)    | D                        |
| Light Kick (LK)     | Q (Select)               |
| Medium Kick (MK)    | W (Cancel)               |
| Heavy Kick (HK)     | E                        |

## Gamepad Controls (Default)

| Action              | Input (Gamepad) |
|---------------------|------------------|
| Move Left           | D-Pad ←          |
| Move Right          | D-Pad →          |
| Crouch              | D-Pad ↓          |
| Jump                | D-Pad ↑          |
| Light Punch (LP)    | X                |
| Medium Punch (MP)   | Y                |
| Heavy Punch (HP)    | RB               |
| Light Kick (LK)     | A                |
| Medium Kick (MK)    | B                |
| Heavy Kick (HK)     | RT               |
| Special Move (e.g., Hadouken) | ↓ ↘ → + Punch |

Notes:
- The default layout follows a common Xbox-style controller mapping.
- In menu scenes:
  - A = Confirm / Select
  - B = Cancel / Back
