import random
import pygame

from scripts.settings import LIGHT_SPEED, STAR_SPEED
from scripts.utils import resource_path


class Celestial(pygame.sprite.Sprite):
    def __init__(self, game, path, x, y):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.scale = random.uniform(2, 4)
        self.image = pygame.transform.scale(
            self.image,
            (int(self.image.get_width() * self.scale),
             int(self.image.get_height() * self.scale))
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = LIGHT_SPEED if game.state.phase_start else STAR_SPEED

    def update(self):
        self.rect = self.image.get_rect(center=self.rect.center)
        self.rect.y += self.speed
        if self.rect.top > pygame.display.Info().current_h:
            self.kill()

class Planet(Celestial):
    def __init__(self, game, x, y):
        super().__init__(game, resource_path(f"assets/galaxies/planet_"
                                       f"{random.randint(1, 10)}.png"), x, y)

class Galaxy(Celestial):
    def __init__(self, game, x, y):
        super().__init__(game, resource_path(f"assets/galaxies/galaxy_"
                                       f"{random.randint(1, 2)}.png"), x, y)

class BlackHole(Celestial):
    def __init__(self, game, x, y):
        super().__init__(game, resource_path(f"assets/galaxies/black_hole_"
                         f"{random.randint(1, 2)}.png"), x, y)

def random_celestial(game):
    screen_w = pygame.display.Info().current_w
    x = random.randint(0, screen_w)
    y = random.randint(-200, -50)

    r = random.random()

    if r > 0.8:
        return Planet(game, x, y)
    elif r > 0.90:
        return Galaxy(game, x, y)
    return None

def is_valid_spawn(new, group, min_dist):
    if new is None:
        return False

    for obj in group:
        if obj is None:
            continue
        dx = new.rect.centerx - obj.rect.centerx
        dy = new.rect.centery - obj.rect.centery
        if dx*dx + dy*dy < min_dist * min_dist:
            return False
    return True