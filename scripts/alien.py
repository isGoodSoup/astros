import random
from typing import override

import pygame

from scripts.levels import DIFFICULTY_ENEMY_SETTINGS
from scripts.proj import Projectile
from scripts.settings import (
    ONE_SECOND, SHIP_HITBOX, ALIEN_HEIGHT, ALIEN_WIDTH,
    SCALE, ALIEN_ADVANTAGE, COLOR_GREEN, ALIEN_COLORS,
    ELITE_DAMAGE_MULT, ELITE_HP_MULT
)
from scripts.utils import resource_path


class Alien(pygame.sprite.Sprite):
    def __init__(self, game, ship, x, y, color, frame, screen=None,
                 width=ALIEN_WIDTH, height=ALIEN_HEIGHT,
                 scale=SCALE / 3, columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.game = game
        self.screen = screen
        self.ship = ship

        self.settings = DIFFICULTY_ENEMY_SETTINGS[self.game.state.difficulty]
        self.width = width
        self.height = height
        self.scale = scale

        self.base_color = color
        self.is_elite = False
        self.elite_applied = False

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.pos = pygame.Vector2(x, y)

        self._apply_color_stats(color)
        self._load_sprite(color)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(
            self.rect.width * SHIP_HITBOX, self.rect.height * SHIP_HITBOX)

        self.direction = "idle"
        self.shooting = False
        self.moving = False
        self.last_shot_time = 0
        self.shot_cooldown = int((ONE_SECOND // 2) / self.settings["fire_rate_multiplier"])
        self.hit = False

    def _apply_color_stats(self, color: str):
        color_scale = ALIEN_COLORS[color]
        self.level = self.ship.level + ALIEN_ADVANTAGE * color_scale
        self.max_hitpoints = int(2 * self.level * self.settings["hp_multiplier"])
        self.base_damage = int(self.ship.damage * self.level * self.settings["damage_multiplier"])

        if self.is_elite:
            self.max_hitpoints = int(self.max_hitpoints * ELITE_HP_MULT)
            self.base_damage *= ELITE_DAMAGE_MULT

        self.hitpoints = self.max_hitpoints

    def _load_sprite(self, color: str):
        image = pygame.image.load(resource_path(f"assets/aliens/{color}.png")).convert_alpha()

        self.image = pygame.transform.scale(image,
            (int(self.width * self.scale), int(self.height * self.scale)))

        if self.is_elite:
            self.image.set_alpha(220)

    def promote_to_elite(self):
        if self.elite_applied:
            return

        self.is_elite = True
        self.elite_applied = True
        current_scale = ALIEN_COLORS[self.base_color]
        higher_tiers = [color for color, scale in ALIEN_COLORS.items()
            if scale > current_scale]

        new_color = random.choice(higher_tiers) if higher_tiers else self.base_color
        self.base_color = new_color

        self._apply_color_stats(new_color)
        center = self.rect.center

        self._load_sprite(new_color)
        self.rect = self.image.get_rect(center=center)

        self.hitbox = self.rect.inflate(
            self.rect.width * SHIP_HITBOX,
            self.rect.height * SHIP_HITBOX)

    def update(self):
        self.sync_hitbox()

        if (self.game.spawns.can_spawn_elites and not self.elite_applied and
                self.hitpoints > 0 and
                self.hitpoints <= self.max_hitpoints * 0.05 and
                random.random() < (self.game.spawns.elite_mutation_chance *
                                   self.settings["elite_chance"])):
            self.promote_to_elite()

        if self.rect.top > pygame.display.Info().current_h or self.hitpoints <= 0:
            self.kill()

    def sync_hitbox(self):
        self.hitbox.center = self.rect.center

    def shoot(self, target, shot_cooldown):
        current_time = pygame.time.get_ticks()
        self.shooting = False
        new_projectiles = []

        direction = pygame.Vector2(0, 1)

        if random.random() > 0.60 and target:
            target_vec = pygame.Vector2(target.rect.center) - pygame.Vector2(
                self.rect.center
            )
            if target_vec.length() != 0:
                direction = target_vec.normalize()

        if current_time - self.last_shot_time >= shot_cooldown:
            projectile = Projectile(
                pos=[self.rect.centerx, self.rect.bottom],
                color=COLOR_GREEN,
                direction=direction,
                speed=12,
                range_limit=900,
                homing=random.choice([True, False]),
                screen=self.screen
            )
            self.shooting = True
            new_projectiles.append(projectile)
            self.last_shot_time = current_time

        return new_projectiles

class KamikazeAlien(Alien):
    def __init__(self, game, ship, x, y, color, frame, screen):
        super().__init__(game, ship, x, y, color, frame, screen)
        self.is_kamikaze = True
        self.ship = ship
        self.speed = 4
        self.locked = False
        self.velocity = pygame.math.Vector2(0, 0)

    @override
    def update(self):
        if not self.locked and random.random() < 0.2:
            self.locked = True

        if self.locked:
            self._home_toward_ship()
        else:
            self.rect.x += 0
            self.rect.y += 0

        self.sync_hitbox()

    def _home_toward_ship(self):
        alien_pos = pygame.math.Vector2(self.rect.center)
        ship_pos = pygame.math.Vector2(self.ship.rect.center)

        direction = ship_pos - alien_pos

        if direction.length() == 0:
            return

        direction = direction.normalize()

        self.velocity = self.velocity.lerp(direction * self.speed, 0.15)

        self.rect.centerx += self.velocity.x
        self.rect.centery += self.velocity.y