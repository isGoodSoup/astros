import random

import pygame

from scripts.proj import Projectile
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
        self.velocity = 0.5
        self.direction = "idle"
        self.shooting = False
        self.moving = False
        self.max_hitpoints = 200
        self.hitpoints = self.max_hitpoints
        self.max_shield = 25
        self.shield = self.max_shield
        self.base_damage = 4
        self.damage = self.base_damage
        self.base_crit_chance = 0.05
        self.crit_chance = self.base_crit_chance
        self.crit_multiplier = 3
        self.evasion = 0.01

        self.maniac_boost = 0
        self.maniac_boost_end = 0

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        self.perk_points = 0
        self.xp_growth = 1.8

    def update_position(self, x, y):
        self.rect.topleft = (x, y)
        self.hitbox.center = self.rect.center

    def shoot(self, base, last_shot_time, shot_cooldown, can_play, sound):
        projectiles = pygame.sprite.Group()
        current_time = pygame.time.get_ticks()
        self.shooting = False
        if current_time - last_shot_time >= shot_cooldown:
            self.shooting = True
            projectile = Projectile(self.rect.centerx, self.rect.top)
            projectiles.add(projectile) # type: ignore
            if can_play:
                sound[0].play()
        return projectiles

    def taken_damage(self):
        return [random.randint(0,10) - 4, random.randint(0,10) - 4]

    def gain_xp(self, amount, sound):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up(sound)

    def level_up(self, sound):
        self.level += 1
        self.damage += 1
        self.max_hitpoints += 10
        self.hitpoints = self.max_hitpoints
        self.max_shield += 10
        self.shield = self.max_shield
        self.perk_points += 1
        self.xp_to_next_level = int(self.xp_to_next_level * self.xp_growth)
        sound[3].play()