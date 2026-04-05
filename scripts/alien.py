from typing import override

import pygame

from scripts.proj import Projectile
from scripts.sheet import SpriteSheet

class Alien(pygame.sprite.Sprite):
    def __init__(self, ship, x, y, frame, width=26, height=32, scale=4,
                 columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.sprite_sheet = SpriteSheet("assets/alien.png")
        self.image = self.sprite_sheet.get_image(frame, width, height, scale, columns)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6,
                                        self.rect.height * -0.6)
        self.ship = ship
        self.velocity = max(1, ship.velocity - 2)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = "idle" # or "left", "right"
        self.shooting = False
        self.moving = False

        self.level = ship.level + 2
        self.max_hitpoints = ship.max_hitpoints * self.level
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = 200
        self.hit = False

    @override
    def update(self):
        self.hitbox.center = self.rect.center

        screen_mid_y = pygame.display.Info().current_h // 2
        target_x = self.ship.rect.centerx + self.offset_x
        target_y = screen_mid_y

        if abs(target_x - self.rect.centerx) > self.velocity:
            self.rect.x += self.velocity if target_x > self.rect.centerx else -self.velocity
        else:
            self.rect.centerx = target_x

        if self.rect.centery < target_y:
            self.rect.y += max(1, self.velocity // 2)
        elif self.rect.centery > target_y:
            self.rect.y -= max(1, self.velocity // 2)
        if self.rect.top > pygame.display.Info().current_h:
            self.kill()

    def shoot(self, base, shot_cooldown, can_play, sound):
        current_time = pygame.time.get_ticks()
        self.shooting = False
        new_projectiles = []

        if current_time - self.last_shot_time >= shot_cooldown:
            projectile = Projectile(self.rect.centerx, self.rect.bottom,
                                    "assets/projectile_3.png", 4, speed=16)
            self.shooting = True
            new_projectiles.extend([projectile])
            self.last_shot_time = current_time
            if can_play:
                sound[0].play()
        return new_projectiles