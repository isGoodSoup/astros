import pygame

# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.

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