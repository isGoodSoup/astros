import pygame

from scripts.settings import FPS, ONE_SECOND


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

        if self.milliseconds >= ONE_SECOND:
            self.milliseconds -= ONE_SECOND
            self.seconds += 1
            if (game.state.current_phase == game.state.phases[-1] and not
            game.state.boss_spawned):
                game.state.current_phase = game.state.phases[
                    game.state.phase_index]
                game.last_alien_spawn = 0
                game.last_asteroid_spawn = 0

            if self.seconds >= FPS:
                self.seconds = 0
                self.minutes += 1
                if self.minutes >= FPS:
                    self.minutes = 0
                    self.hours += 1