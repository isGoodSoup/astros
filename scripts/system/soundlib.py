import pygame

from scripts.engine.utils import resource_path
from scripts.system.config import save_config

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
        "journey": resource_path("assets/fx/journey.ogg"),
    }

def _music_volume_up(game, step=0.1):
    game.mixer.music_volume = min(game.mixer.music_volume + step, 1.0)
    apply_volume(game)
    save_config(game)

def _music_volume_down(game, step=0.1):
    game.mixer.music_volume = max(game.mixer.music_volume - step, 0.0)
    apply_volume(game)
    save_config(game)

def _sfx_volume_up(game, step=0.1):
    game.mixer.sfx_volume = min(game.mixer.sfx_volume + step, 1.0)
    apply_volume(game)
    save_config(game)

def _sfx_volume_down(game, step=0.1):
    game.mixer.sfx_volume = max(game.mixer.sfx_volume - step, 0.0)
    apply_volume(game)
    save_config(game)

def apply_volume(game):
    for sound in game.mixer.sounds:
        sound.set_volume(game.mixer.sfx_volume)
    pygame.mixer.music.set_volume(game.mixer.music_volume)