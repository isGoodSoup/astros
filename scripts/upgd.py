import random
from typing import override

import pygame

upgrades = ["assets/power_up.png", "assets/shield.png"]
def get_upgrade():
    return random.choice(upgrades)

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, path, x, y, scale=3):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image,(self.image.get_width() * scale,
                                             self.image.get_height() * scale))
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.x, self.y = x, y
        self.speed = 6

    @override
    def update(self):
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()