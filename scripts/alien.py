import random

import pygame

from scripts.proj import Projectile
from scripts.settings import ONE_SECOND, SHIP_HITBOX, ALIEN_HEIGHT, ALIEN_WIDTH, \
    SCALE, ALIEN_ADVANTAGE, COLOR_GREEN, ALIEN_COLORS
from scripts.utils import resource_path


class Alien(pygame.sprite.Sprite):
    def __init__(self, ship, x, y, color, frame, screen=None,
                 width=ALIEN_WIDTH, height=ALIEN_HEIGHT,
                 scale=SCALE/3, columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.screen = screen
        self.image = pygame.image.load(resource_path(f"assets/aliens/{color}.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * SHIP_HITBOX, self.rect.height * SHIP_HITBOX)
        self.pos = pygame.Vector2(x, y)
        self.frames = []
        self.ship = ship
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = "idle"
        self.shooting = False
        self.moving = False

        self.level = ship.level + ALIEN_ADVANTAGE * ALIEN_COLORS[color]
        self.max_hitpoints = 2 * self.level
        self.hitpoints = self.max_hitpoints
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = ONE_SECOND // 2
        self.hit = False

    def update(self):
        self.hitbox.center = self.rect.center
        if self.rect.top > pygame.display.Info().current_h or self.hitpoints <= 0:
            self.kill()

    def shoot(self, target, shot_cooldown):
        current_time = pygame.time.get_ticks()
        self.shooting = False
        new_projectiles = []

        direction = (0, 1)
        if random.random() > 0.60:
            target_vec = pygame.Vector2(self.ship.rect.center) - pygame.Vector2(
                self.rect.center)
            if target_vec.length() != 0:
                direction = target_vec.normalize()
            else:
                direction = pygame.Vector2(0, 1)

            angle_offset = random.uniform(-0.2, 0.2)

        if current_time - self.last_shot_time >= shot_cooldown:
            projectile = Projectile(
                pos=[self.rect.centerx, self.rect.bottom],
                color=COLOR_GREEN, direction=direction, speed=12,
                range_limit=900, homing=random.choice([True, False]),
                screen=self.screen)
            self.shooting = True
            new_projectiles.extend([projectile])
            self.last_shot_time = current_time
        return new_projectiles