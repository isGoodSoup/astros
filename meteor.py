import random
from typing import override

import pygame

class Meteor(pygame.sprite.Sprite):
    def __init__(self, screen_width, min_y=-150, max_y=0, scale=3, speed=8):
        super().__init__()
        self.image = pygame.image.load("assets/meteor.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, [self.image.get_width() * scale,
                                                         self.image.get_height() * scale])
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(min_y, max_y)
        self.hitbox = self.rect.copy()
        self.speed = speed

    @override
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
        self.hitbox.topleft = self.rect.topleft