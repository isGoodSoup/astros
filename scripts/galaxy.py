import random

import pygame

class Celestial(pygame.sprite.Sprite):
    def __init__(self, path, x, y):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 1

    def update(self):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.speed
        if self.rect.top < pygame.display.Info().current_h:
            self.kill()

class Planet(Celestial):
    def __init__(self, x, y):
        super().__init__(f"assets/galaxies/planet_"
                                       f"{random.randint(1, 10)}.png", x, y)

class Galaxy(Celestial):
    def __init__(self, x, y):
        super().__init__(f"assets/galaxies/galaxy_"
                                       f"{random.randint(1, 2)}", x, y)

class BlackHole(Celestial):
    def __init__(self, x, y):
        super().__init__(f"assets/galaxies/black_hole_"
                         f"{random.randint(1, 2)}.png", x, y)