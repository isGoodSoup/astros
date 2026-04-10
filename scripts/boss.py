import math
import random

import pygame

from scripts.proj import Projectile

class Boss(pygame.sprite.Sprite):
    def __init__(self, ship, projectiles, x, y, color, frame=0, width=32,
                 height=32, scale=8, columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.image = pygame.image.load(f"assets/aliens/{color}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.rect = self.image.get_rect(center=(x,y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.5, self.rect.height * -0.5)

        self.pos = pygame.Vector2(x, y)
        self.ship = ship
        self.step = max(1, ship.velocity + 1)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = 1
        self.shooting = False
        self.moving = False

        self.colors = {'red' : 100, 'green' : 200, 'yellow' : 300}
        self.level = ship.level + 20
        self.max_hitpoints = 100 * self.level + self.colors.get(color)
        self.hitpoints = self.max_hitpoints
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = 150
        self.last_move = pygame.time.get_ticks()
        self.move_timer = pygame.time.get_ticks()
        self.hit = False
        self.boss_phases = ['phase1', 'phase2', 'phase3']
        self.current_phase = self.boss_phases[0]
        self.phase_index = 0

        self.velocity = pygame.Vector2(
            random.choice([-1, 1]) * random.uniform(3, 6),
            random.choice([-1, 1]) * random.uniform(3, 6)
        )
        self.phase2_change_time = pygame.time.get_ticks()
        self.phase2_change_interval = 1000

        self.projectiles = projectiles

        self.target = pygame.Vector2(
            self.ship.rect.midbottom[0] + self.offset_x,
            self.offset_y
        )

    def update(self):
        self.hitbox.center = self.rect.center
        now = pygame.time.get_ticks()

        if self.current_phase == 'phase1':
            screen_width = pygame.display.Info().current_w
            screen_height = pygame.display.Info().current_h
            if self.rect.right >= screen_width or self.rect.left <= 0:
                self.direction *= -1
                self.rect.y += 30 if not self.rect.y <= screen_height else 30

            self.rect.x += self.direction * self.step
            self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width))
            self.move_timer = now

            if random.random() > 0.5:
                if now - self.last_shot_time >= self.shot_cooldown:
                    self.last_shot_time = now
                    self.shoot()

        if self.current_phase == 'phase2':
            screen = pygame.display.get_surface()
            screen_width, screen_height = screen.get_size()

            if now - self.phase2_change_time > self.phase2_change_interval:
                self.velocity.x += random.uniform(-2, 2)
                self.velocity.y += random.uniform(-2, 2)

                max_speed = 16
                if self.velocity.length() > max_speed:
                    self.velocity.scale_to_length(max_speed)

                self.phase2_change_time = now

            self.rect.x += int(self.velocity.x)
            self.rect.y += int(self.velocity.y)

            if self.rect.left <= 0:
                self.rect.left = 0
                self.velocity.x *= -1
            elif self.rect.right >= screen_width:
                self.rect.right = screen_width
                self.velocity.x *= -1

            if self.rect.top <= 0:
                self.rect.top = 0
                self.velocity.y *= -1
            elif self.rect.bottom >= screen_height:
                self.rect.bottom = screen_height
                self.velocity.y *= -1

            if now - self.last_shot_time >= self.shot_cooldown:
                self.last_shot_time = now
                self.shoot()

        if self.current_phase == 'phase3':
            screen = pygame.display.get_surface()
            screen_width, screen_height = screen.get_size()

            if now - self.phase2_change_time > self.phase2_change_interval:
                self.velocity.x += random.uniform(-4, 4)
                self.velocity.y += random.uniform(-4, 4)

                max_speed = 32
                if self.velocity.length() > max_speed:
                    self.velocity.scale_to_length(max_speed)

                self.phase2_change_time = now

            self.rect.x += int(self.velocity.x)
            self.rect.y += int(self.velocity.y)

            if self.rect.left <= 0:
                self.rect.left = 0
                self.velocity.x *= -1
            elif self.rect.right >= screen_width:
                self.rect.right = screen_width
                self.velocity.x *= -1

            if self.rect.top <= 0:
                self.rect.top = 0
                self.velocity.y *= -1
            elif self.rect.bottom >= screen_height:
                self.rect.bottom = screen_height
                self.velocity.y *= -1

            if now - self.last_shot_time >= self.shot_cooldown:
                self.last_shot_time = now
                self.shoot()

        health_ratio = self.hitpoints / self.max_hitpoints
        if health_ratio < 0.7 and self.current_phase == 'phase1':
            self.current_phase = 'phase2'
        elif health_ratio < 0.5 and self.current_phase == 'phase2':
            self.current_phase = 'phase3'

    def shoot(self):
        target_vec = pygame.Vector2(self.ship.rect.center) - pygame.Vector2(
            self.rect.center)
        if target_vec.length() != 0:
            direction = target_vec.normalize()
        else:
            direction = pygame.Vector2(0, 1)

        angle_offset = random.uniform(-0.2, 0.2)

        direction.rotate_ip(math.degrees(angle_offset))
        self.projectiles.add(Projectile(self.rect.center, (255, 0, 0),
                          direction=(direction.x, direction.y),
                          speed=16,
                          damage=100 * self.ship.level,
                          range_limit=1000))