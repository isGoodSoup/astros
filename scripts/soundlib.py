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
    sounds.append(pygame.mixer.Sound("assets/fx/critical.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/game_over.ogg"))
    return sounds

def load_ost():
    return {
        "theme": "assets/fx/theme.ogg",
        "flight": "assets/fx/flight.ogg",
    }

def increase_volume(game):
    game.volume = min(game.volume + 0.1, 1.0)
    apply_volume(game)
    game.save_config()

def decrease_volume(game):
    game.volume = max(game.volume - 0.1, 0.0)
    apply_volume(game)
    game.save_config()

def apply_volume(game):
    for sound in game.sounds:
        sound.set_volume(game.volume)
    pygame.mixer.music.set_volume(game.volume)