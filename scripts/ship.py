import random

import pygame

from scripts.sheet import SpriteSheet

class Ship(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, x, y, frame, width, height, scale=4,
                 columns=1):
        super().__init__()
        self.sprite_sheet = SpriteSheet("assets/ship.png")
        self.image = sprite_sheet.get_image(frame, width, height, scale, columns)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6,
                                        self.rect.height * -0.6)
        self.velocity = 12
        self.direction = "idle"
        self.shooting = False
        self.moving = False
        self.max_hitpoints = 280
        self.max_shield = 25
        self.hitpoints = self.max_hitpoints
        self.shield = self.max_shield
        self.damage = 4
        self.crit = self.damage * 2

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.perk_points = 0
        self.xp_growth = 1.5

    def update_position(self, x, y):
        self.rect.topleft = (x, y)
        self.hitbox.center = self.rect.center

    def taken_damage(self):
        return [random.randint(0,10) - 4, random.randint(0,10) - 4]

    def gain_xp(self, amount, sound):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up(sound)

    def level_up(self, sound):
        self.level += 1
        self.perk_points += 1
        self.xp_to_next_level = int(self.xp_to_next_level * self.xp_growth)
        sound[3].play()