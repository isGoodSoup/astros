import pygame
import random

import scripts.assets as assets
from scripts.constants import *
from scripts.entity import DepthEntity


class Asteroid(DepthEntity):
    def __init__(self, x, y, z):
        image = random.choice(assets.ASTEROID_SPRITES)
        super().__init__(image, x, y, z)
        self.world_pos = pygame.Vector2(x, y)
        self.speed = 4
        self.base_image = self.image
        self.hitpoints = ASTEROID_HITPOINTS

    def update(self):
        self.z -= self.speed * 2

        if self.z <= 1:
            self.kill()