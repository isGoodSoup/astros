import random

import pygame

from scripts.update import spawn_boss
from scripts.utils import level_enemies

class Clock:
    def __init__(self):
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.milliseconds = 0
        self.stopwatch = None

    def update_time(self, game):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - getattr(game, 'last_time', 0)
        if not hasattr(game, 'last_time'):
            game.last_time = current_time
            return

        self.milliseconds += elapsed
        game.last_time = current_time

        if self.milliseconds >= 1000:
            self.milliseconds -= 1000
            self.seconds += 1
            if self.seconds % random.randint(20, 30) == 0:
                if (game.state.current_phase == game.state.phases[-1] and not
                game.state.boss_spawned):
                    spawn_boss(game)
                    game.state.boss_alive = True
                    game.state.boss_spawned = True
                else:
                    if (game.state.current_phase == game.state.phases[0] and not
                    game.aliens):
                        pass
                    else:
                        game.state.phase_index = (game.state.phase_index + 1) % len(
                            game.state.phases)
                        game.state.current_phase = game.state.phases[game.state.phase_index]
                        game.last_alien_spawn = 0
                        game.last_asteroid_spawn = 0
                        if game.state.current_phase in game.state.phases:
                            level_enemies(game)
            if self.seconds >= 60:
                self.seconds = 0
                self.minutes += 1
                if self.minutes >= 60:
                    self.minutes = 0
                    self.hours += 1