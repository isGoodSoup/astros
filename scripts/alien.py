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
        self.direction = "idle"
        self.shooting = False
        self.moving = False

        self.level = ship.level + 2
        self.max_hitpoints = ship.max_hitpoints * self.level
        self.hitpoints = self.max_hitpoints
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = 200
        self.move_delay = 200
        self.hit = False

    @override
    def update(self):
        self.hitbox.center = self.rect.center
        target_x = self.ship.rect.centerx + self.offset_x
        target_y = self.offset_y

        dx = target_x - self.rect.x
        if abs(dx) > self.velocity:
            self.rect.x += self.velocity if dx > 0 else -self.velocity
        else:
            self.rect.x = target_x

        dy = target_y - self.rect.y
        if abs(dy) > 1:
            self.rect.y += dy / abs(dy) * max(1, self.velocity // 2)
        else:
            self.rect.y = target_y

        if self.rect.top > pygame.display.Info().current_h or self.hitpoints <= 0:
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