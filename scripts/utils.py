import datetime
import functools
import os
import sys

import pygame

from scripts.floaty import FloatingNumber


def legacy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__legacy__ = True
    return wrapper

def formulize(game, level, base_xp=5):
    score_factor = game.state.score ** 0.5
    return int(base_xp * (level ** 1.2) + score_factor)

def add_multiplier(game, x, y, text, color=(255, 255, 0), font_size=24):
    offset = 0
    for fn in game.sprites.floating_numbers:
        if abs(fn.rect.centerx - x) < 50 and abs(
                fn.rect.centery - y - offset) < 5:
            offset -= 30
    game.sprites.floating_numbers.add(FloatingNumber(x, y + offset, text, game.font, color=color, # type: ignore
                       font_size=font_size))

def debug(game):
    game.state.debugging = not game.debugging

def apply_curve(game, v):
    return v * abs(v)

def center(game, text, screen_size):
    return screen_size[0] // 2 - text.get_width() // 2

def take_screenshot(game):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    home_dir = os.path.expanduser("~")
    save_dir = os.path.join(home_dir, ".imgs")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{timestamp}.png")
    game.crt.ctx.finish()
    data = game.crt.ctx.screen.read(components=4)
    surface = pygame.image.fromstring(data,game.screen_size,
        "RGBA",
        True)
    pygame.image.save(surface, save_path)

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.abspath(".")
    return os.path.join(base, relative_path)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    line = ""

    for word in words:
        test = f"{line} {word}".strip()
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)

    return lines