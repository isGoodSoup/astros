import random

import pygame
from scripts.utils import level_enemies

def update_time(game):
    current_time = pygame.time.get_ticks()
    elapsed = current_time - getattr(game, 'last_time', 0)
    if not hasattr(game, 'last_time'):
        game.last_time = current_time
        return

    game.milliseconds += elapsed
    game.last_time = current_time

    if game.milliseconds >= 1000:
        game.milliseconds -= 1000
        game.seconds += 1
        if game.seconds % random.randint(20, 30) == 0:
            if game.current_phase == "boss_fight" and not game.boss_spawned:
                game.spawn_boss()
                game.boss_alive = True
                game.boss_spawned = True
            else:
                game.phase_index = (game.phase_index + 1) % len(game.phases)
                game.current_phase = game.phases[game.phase_index]
                game.last_alien_spawn = 0
                game.last_asteroid_spawn = 0
                if game.current_phase == "asteroids":
                    level_enemies(game)
                game.stars_speed += 1
        if game.seconds >= 60:
            game.seconds = 0
            game.minutes += 1
            if game.minutes >= 60:
                game.minutes = 0
                game.hours += 1