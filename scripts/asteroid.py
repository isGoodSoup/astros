import random
from typing import override

import pygame

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen_width, min_y=-150, max_y=0,
                 scale=random.randint(2, 4), speed=8):
        super().__init__()
        self.asteroids = [1,2,3,4,5,7,8]
        self.image = pygame.image.load(f"assets/asteroids/asteroid"
                                       f"_{random.choice(self.asteroids)}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, [self.image.get_width() * scale,
                                                         self.image.get_height() * scale])
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(min_y, max_y)
        self.hitbox = self.rect.inflate(self.rect.width * -0.7,self.rect.height * -0.7)
        self.speed = speed
        self.hitpoints = 8

    @override
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
        self.hitbox.center = self.rect.center