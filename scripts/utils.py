import datetime
import os

import pygame

from scripts.floaty import FloatingNumber

def formulize(game, level, base_xp=5):
    score_factor = game.state.score ** 0.5
    return int(base_xp * (level ** 1.2) + score_factor)

def add_multiplier(game, x, y, text, color=(255, 255, 0), font_size=24):
    offset = 0
    for fn in game.floating_numbers:
        if abs(fn.rect.centerx - x) < 50 and abs(
                fn.rect.centery - y - offset) < 5:
            offset -= 30
    game.floating_numbers.add(
        FloatingNumber(x, y + offset, text, game.font, color=color, # type: ignore
                       font_size=font_size))

def level_enemies(game):
    for asteroid in game.asteroids:
        game.asteroid_hitpoints = 1 + 0.1 * game.ship.level
        game.asteroid_speed = 1 + 10 * game.ship.level

def debug(game):
    game.state.debugging = not game.debugging

def apply_curve(game, v):
    return v * abs(v)

def center(game, text, screen_size):
    return screen_size[0] // 2 - text.get_width() // 2

def take_screenshot(self, screen):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    home_dir = os.path.expanduser("~")
    save_dir = os.path.join(home_dir, ".imgs")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{timestamp}.png")
    pygame.image.save(screen, save_path)