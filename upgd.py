import random
from typing import override

import pygame

upgrades = ["assets/power_up.png", "assets/shield.png"]
def get_upgrade():
    return random.choice(upgrades)

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, path, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.x, self.y = x, y
        self.speed = 6

    @override
    def update(self):
        self.y -= self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()