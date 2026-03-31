import random
import pygame

class Celestial(pygame.sprite.Sprite):
    def __init__(self, path, x, y, speed=1):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.scale = random.uniform(0.5, 1.5)
        self.image = pygame.transform.scale(
            self.image,
            (int(self.image.get_width() * self.scale),
             int(self.image.get_height() * self.scale))
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.speed
        if self.rect.top > pygame.display.Info().current_h:
            self.kill()

class Planet(Celestial):
    def __init__(self, x, y):
        super().__init__(f"assets/galaxies/planet_"
                                       f"{random.randint(1, 10)}.png", x, y)

class Galaxy(Celestial):
    def __init__(self, x, y):
        super().__init__(f"assets/galaxies/galaxy_"
                                       f"{random.randint(1, 2)}.png", x, y)

class BlackHole(Celestial):
    def __init__(self, x, y):
        super().__init__(f"assets/galaxies/black_hole_"
                         f"{random.randint(1, 2)}.png", x, y)

def random_celestial():
    screen_w = pygame.display.Info().current_w
    x = random.randint(0, screen_w)
    y = random.randint(-200, -50)

    r = random.random()

    if r < 0.6:
        return Planet(x, y)
    elif r < 0.9:
        return Galaxy(x, y)
    else:
        return BlackHole(x, y)