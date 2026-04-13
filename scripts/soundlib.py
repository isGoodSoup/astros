import pygame

from scripts.utils import resource_path

# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.

sounds = []

def load_sounds():
    sounds.clear()
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/beam.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/explosion.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/power_up.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/level_up.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/menu.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/select.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/critical.ogg")))
    sounds.append(pygame.mixer.Sound(resource_path("assets/fx/game_over.ogg")))
    return sounds

def load_ost():
    return {
        "odyssey": resource_path("assets/fx/odyssey.ogg"),
        "flight": resource_path("assets/fx/flight.ogg"),
        "unknown": resource_path("assets/fx/unknown.ogg"),
        "starfield": resource_path("assets/fx/starfield.ogg"),
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
    for sound in game.mixer.sounds:
        sound.set_volume(game.volume)
    pygame.mixer.music.set_volume(game.volume)