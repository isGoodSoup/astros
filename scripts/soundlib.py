import pygame

# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.
# All assets in this game are © 2026 Diego. See ASSETS_LICENSE.txt.

sounds = []

def load_sounds():
    sounds.append(pygame.mixer.Sound("assets/fx/beam.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/explosion.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/power_up.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/level_up.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/menu.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/game_over.ogg"))
    return sounds

def load_ost():
    return pygame.mixer.music.load("assets/fx/theme.ogg")

VOLUME_STEP = 0.1

def increase_volume():
    for sound in sounds:
        new_vol = min(sound.get_volume() + VOLUME_STEP, 1.0)
        sound.set_volume(new_vol)
    pygame.mixer.music.set_volume(min(pygame.mixer.music.get_volume() + VOLUME_STEP, 1.0))

def decrease_volume():
    for sound in sounds:
        new_vol = max(sound.get_volume() - VOLUME_STEP, 0.0)
        sound.set_volume(new_vol)
    pygame.mixer.music.set_volume(max(pygame.mixer.music.get_volume() - VOLUME_STEP, 0.0))