import random

import pygame

class Planet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(f"../assets/galaxies/planet_"
                                       f"{random.randint(1, 10)}.png")
        self.rect = self.image.get_rect(center=(0,0))
        self.speed = 1

    def update(self):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.speed
        if self.rect.top < pygame.display.Info().current_h:
            self.kill()

class Galaxy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(f"../assets/galaxies/galaxy_"
                                       f"{random.randint(1, 2)}")
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 1

    def update(self):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.speed
        if self.rect.top < pygame.display.Info().current_h:
            self.kill()

class BlackHole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(f"../assets/galaxies/black_hole_"
                                       f"{random.randint(1, 2)}.png")
        self.rect = self.image.get_rect(center=(x,y))
        self.speed = 1

    def update(self):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.speed
        if self.rect.top < pygame.display.Info().current_h:
            self.kill()