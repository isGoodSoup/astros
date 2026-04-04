import random

import pygame

from scripts.explode import Explosion
from scripts.proj import Projectile


class Ship(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, x, y, frame, width, height, scale=4,
                 columns=1):
        super().__init__()
        self.image = sprite_sheet.get_image(frame, width, height, scale, columns)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6,
                                        self.rect.height * -0.6)
        self.velocity = 12
        self.direction = "idle" # or "left", "right"
        self.shooting = False
        self.moving = False
        self.max_hitpoints = 200
        self.hitpoints = self.max_hitpoints
        self.max_shield = 25
        self.base_max_shield = self.max_shield
        self.shield = self.max_shield
        self.gun = "beam" # or "missile"
        self.base_damage = 4
        self.damage = self.base_damage
        self.damage_multiplier = 1.0
        self.base_crit_chance = 0.05
        self.crit_chance = self.base_crit_chance
        self.crit_multiplier = 3

        self.base_charges = 3
        self.charges = self.base_charges
        self.base_ammo = 100
        self.ammo = self.base_ammo
        self.evasion = 0.01
        self.shot_cooldown = 300

        self.maniac_boost = 0
        self.maniac_boost_end = 0

        self.tower_boost = 0
        self.tower_boost_end = 0
        self.tower_boost_applied = False

        self.fortified_percent = 0
        self.fortified_cap = 200

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 256
        self.perk_points = 0
        self.xp_growth = 2.0
        self.credits = 0

        self.hit = False
    def update_damage(self):
        base = self.base_damage * (2 if self.gun == "missile" else 1)
        self.damage = base * self.damage_multiplier

    def update_position(self, x, y):
        self.rect.topleft = (x, y)
        self.hitbox.center = self.rect.center

    def shoot(self, base, last_shot_time, shot_cooldown, can_play, sound):
        self.update_damage()
        current_time = pygame.time.get_ticks()
        self.shooting = False
        new_projectiles = []

        if current_time - last_shot_time >= shot_cooldown:
            self.shooting = True
            offset = 30
            left_x = self.rect.centerx - offset
            right_x = self.rect.centerx + offset
            y = self.rect.bottom
            projectile = Projectile(left_x, y,"assets/projectile_2.png" if self.gun == "missile" else "assets/projectile.png")
            projectile_2 = Projectile(right_x, y,"assets/projectile_2.png" if self.gun == "missile" else "assets/projectile.png")
            new_projectiles.extend([projectile, projectile_2])
            if can_play:
                sound[0].play()

            if self.gun == "missile":
                self.ammo -= 1

        return new_projectiles

    def super_charge(self, joysticks, score, explosions, asteroids,
                             frame_explode, frame_big_explode):
        if self.charges <= 0:
            return

        if joysticks:
            joysticks[0].rumble(0.5, 1.0, 1000)
        explosions.add(Explosion(self.hitbox.centerx, self.hitbox.centery, frame_big_explode))

        for asteroid in asteroids:
            asteroid.kill()
            explosions.add(Explosion(asteroid.rect.centerx, asteroid.rect.centery, frame_explode))
            score += self.level * 10

        self.charges -= 1

    def taken_damage(self):
        return [random.randint(0,10) - 4, random.randint(0,10) - 4]

    def gain_xp(self, amount, sound):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up(sound)

    def level_up(self, sound):
        self.level += 1
        self.base_damage += 1
        self.max_hitpoints += 10
        self.hitpoints = self.max_hitpoints
        self.max_shield += 10
        self.shield = self.max_shield
        self.perk_points += 1
        self.xp_to_next_level = int(self.xp_to_next_level * self.xp_growth)
        sound[3].play()

    def get_stats(self):
        return {
            "level": self.level,
            "xp": self.xp,
            "perk_points": self.perk_points,
            "hitpoints": self.hitpoints,
            "shield": self.shield,
            "damage": self.damage,
            "crit_chance": self.crit_chance,
            "crit_multiplier": self.crit_multiplier,
            "velocity": self.velocity,
            "max_hitpoints": self.max_hitpoints,
            "max_shield": self.max_shield,
        }