import random
from typing import override

import pygame

import scripts.assets as assets
from scripts.constants import *

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen_width, min_y=-150, max_y=0,
                 scale=random.randint(1, SCALE), speed=8):
        super().__init__()
        self.image = random.choice(assets.ASTEROID_SPRITES)
        self.image = pygame.transform.scale(self.image,
            (self.image.get_width() * scale, self.image.get_height() * scale))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(min_y, max_y)
        self.hitbox = self.rect.inflate(self.rect.width * -0.7,self.rect.height * -0.7)
        self.speed = speed
        self.hitpoints = ASTEROID_HITPOINTS

    @override
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
        self.hitbox.center = self.rect.center