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
            game.sprites.last_time = current_time
            return

        self.milliseconds += elapsed
        game.sprites.last_time = current_time

        if self.milliseconds >= ONE_SECOND:
            self.milliseconds -= ONE_SECOND
            self.seconds += 1
            if self.seconds >= FPS:
                self.seconds = 0
                self.minutes += 1
                if self.minutes >= FPS:
                    self.minutes = 0
                    self.hours += 1