import pygame

class Fade:
    def __init__(self, duration=1000):
        self.duration = duration
        self.start_time = None
        self.active = False
        self.mode = "in"

    def start(self, mode="out"):
        self.mode = mode
        self.start_time = pygame.time.get_ticks()
        self.active = True

    def update(self):
        if not self.active:
            return 0

        elapsed = pygame.time.get_ticks() - self.start_time
        t = min(1.0, elapsed / self.duration)

        if self.mode == "out":
            alpha = int(255 * t)
        else:
            alpha = int(255 * (1 - t))

        if t >= 1.0:
            self.active = False
        return alpha

fade = Fade()