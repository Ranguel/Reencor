# Reencor
 
A retro-inspired 2D fighting game featuring classic-style sprites, Pygame, and OpenGL.

## Demo Video

Check out the gameplay demo on Reddit:  
[View the demo here](https://www.reddit.com/r/pygame/comments/1ksj3po/just_added_combo_trials_mode_to_my_fighting_game/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

## Version

**Version:** 0.3.2-pre.1

## Features

- Classic 2D fighting mechanics
- Keyboard and joystick support
- OpenGL rendering

## Requirements

- Python 3.9+
- [Pygame](https://www.pygame.org/)
- [PyOpenGL](http://pyopengl.sourceforge.net/)

## Sprites

This game uses character sprites from *Street Fighter III* and *SNK vs Capcom* for educational purposes only.

You can download the sprites from the following source:

- [Ryu Street Fighter III (Sprite Sets)](https://www.nowak.ca/zweifuss/all/02_Ryu.zip)
- [Ken Street Fighter III (Sprite Sets)](https://www.nowak.ca/zweifuss/all/11_Ken.zip)
- [Ingame effects Street Fighter III (Sprite Sets)](https://www.justnopoint.com/zweifuss/all/22_Ingame%20Effects.zip)
- [SNK vs Capcom - Haohmaru (The Spriters Resource)](https://www.spriters-resource.com/download/42408/)
- [SNK vs Capcom - Terry Bogard (The Spriters Resource)](https://www.spriters-resource.com/download/42433/)

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
| Light Kick (LK)     | Q                        |
| Medium Kick (MK)    | W                        |
| Heavy Kick (HK)     | E                        |
| Special Move (e.g., Hadouken) | ↓ ↘ → + Punch |

## How to Run

```bash
git clone https://github.com/Ranguel/Reencor
cd Reencor
python main.py
