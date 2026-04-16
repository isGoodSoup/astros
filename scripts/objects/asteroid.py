import random
from typing import override

import pygame

import scripts.system.assets as assets
from scripts.system.constants import *


class Asteroid(pygame.sprite.Sprite):
    def __init__(self, screen_width, min_y=-150, max_y=0,
                 scale=random.randint(1, SCALE), speed=8):
        super().__init__()
        self.original_image = random.choice(assets.ASTEROID_SPRITES)
        self.original_image = pygame.transform.scale(self.original_image,
            (self.original_image.get_width() * scale, self.original_image.get_height() * scale))
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(min_y, max_y)
        self.hitbox = self.rect.inflate(self.rect.width * -0.7,self.rect.height * -0.7)
        self.speed = speed
        self.hitpoints = ASTEROID_HITPOINTS
        self.hit_flash_timer = 0
        self.hit_flash_duration = 8

    def trigger_hit_flash(self):
        self.hit_flash_timer = self.hit_flash_duration

    def update_hit_flash(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            if self.hit_flash_timer > self.hit_flash_duration - 2:
                self.image = self.flash_image
            elif (self.hit_flash_timer // 2) % 2 == 0:
                self.image = self.flash_image
            else:
                self.image = self.original_image
        else:
            self.image = self.original_image

    @override
    def update(self):
        self.update_hit_flash()
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
        self.hitbox.center = self.rect.center