import datetime
import functools
import os
import random
import sys

import pygame

from scripts.floaty import FloatingNumber
from scripts.constants import SETTINGS_DEFINITION, SCREENSHOTS_DIR
from scripts.shared import fade
from scripts.config import save_config

def legacy(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    wrapper.__legacy__ = True
    return wrapper

def formulize(game, level, base_xp=5):
    score_factor = game.state.score ** 0.5
    return int(base_xp * (level ** 1.2) + score_factor)

def activate_shield_regen(ship, duration_ms: int):
    ship.shield_regen = True
    ship.shield_regen_end = pygame.time.get_ticks() + duration_ms

def add_multiplier(game, x, y, text, color=(255, 255, 0), font_size=24):
    offset = 0
    for fn in game.sprites.floating_numbers:
        if abs(fn.rect.centerx - x) < 50 and abs(
                fn.rect.centery - y - offset) < 5:
            offset -= 30
    game.sprites.floating_numbers.add(FloatingNumber(x, y + offset, text, game.font,
            color=color, font_size=font_size))

def debug(game):
    game.state.debugging = not game.debugging

def apply_curve(game, v):
    return v * abs(v)

def random_pos(game):
    return (random.randint(0, game.screen_size[0]),
            random.randint(-100, game.screen_size[1]))

def center(game, text, screen_size):
    return screen_size[0] // 2 - text.get_width() // 2

def take_screenshot(game):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    home_dir = os.path.expanduser("~")
    save_dir = os.path.join(home_dir, SCREENSHOTS_DIR)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{timestamp}.png")
    game.crt.ctx.finish()
    data = game.crt.ctx.screen.read(components=4)
    surface = pygame.image.fromstring(data,game.screen_size,"RGBA", True)
    pygame.image.save(surface, save_path)

def toggle_setting(game, index):
    setting = SETTINGS_DEFINITION[index]

    if setting.get("type") != "toggle":
        return

    target = _get_setting_target(game, setting)
    key = setting["key"]

    new_value = not getattr(target, key)
    setattr(target, key, new_value)
    save_config(game)

def _get_setting_target(game, setting):
    target_name = setting.get("target", "state")
    return getattr(game, target_name)

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

def render_fade(screen, screen_size):
    alpha = fade.update()
    if alpha > 0:
        fade_surface = pygame.Surface(screen_size)
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
    return alpha