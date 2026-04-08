import math
import random

import pygame

from scripts.explode import Explosion
from scripts.proj import Projectile
from scripts.toggles import unlimited_ammo


class Ship(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, x, y, frame, width, height, scale=4,
                 columns=1):
        super().__init__()
        self.image = sprite_sheet.get_image(frame, width, height, scale, columns)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6, self.rect.height * -0.6)
        self.velocity = 12
        self.direction = "idle"
        self.shooting = False
        self.moving = False
        self.max_hitpoints = 200
        self.hitpoints = self.max_hitpoints
        self.max_shield = 25
        self.base_max_shield = self.max_shield
        self.shield = self.max_shield
        self.gun_order = ["beam", "shotgun", "auto"]
        self.gun = "beam"
        self.guns = {"beam": 250, "shotgun": 400, "auto": 150}
        self.base_damage = 4
        self.damage = self.base_damage
        self.damage_multiplier = 1.0
        self.base_crit_chance = 0.05
        self.crit_chance = self.base_crit_chance
        self.crit_multiplier = 3

        self.base_charges = 1
        self.charges = self.base_charges
        self.base_ammo = 200
        self.ammo = self.base_ammo
        self.evasion = 0.01
        self.shot_cooldown = 250

        self.maniac_boost = 0
        self.maniac_boost_end = 0

        self.tower_boost = 0
        self.tower_boost_end = 0
        self.tower_boost_applied = False

        self.fortified_percent = 0
        self.fortified_cap = 200

        self.skills = []

        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 256
        self.perk_points = 0
        self.xp_growth = 2.0
        self.credits = 0

        self.hit = False
        self.critical = False

    def add_skill(self, skill):
        self.skills.append(skill)

    def update_damage(self):
        base = self.base_damage
        if self.gun == "shotgun":
            base *= 10

    def update_fire_rate(self):
        self.shot_cooldown = self.guns[self.gun]

    def update_position(self, x, y):
        self.rect.topleft = (x, y)
        self.hitbox.center = self.rect.center

    def switch_gun(self):
        idx = self.gun_order.index(self.gun)
        self.gun = self.gun_order[(idx + 1) % len(self.gun_order)]
        self.update_damage()
        self.update_fire_rate()

    def shoot(self, gun_type=None):
        if gun_type is None:
            gun_type = self.gun

        projectiles = []
        pos = self.hitbox.center
        if gun_type == "beam":
            projectiles.append(
                Projectile(pos, (255, 255, 0), direction=(0, -1), speed=16,
                           damage=1))

        elif gun_type == "shotgun":
            if self.ammo <= 0:
                return projectiles

            num_pellets = 6
            spread_angle = 30
            for i in range(num_pellets):
                angle = (-spread_angle / 2) + (i * (spread_angle / (num_pellets - 1)))
                rad = math.radians(angle)
                direction = (math.sin(rad), -math.cos(rad))
                proj = Projectile(pos, (255, 200, 0), direction=direction,
                                  speed=12, damage=3, range_limit=200)
                projectiles.append(proj)
            if not unlimited_ammo:
                self.ammo -= num_pellets

        if gun_type == "auto":
            if self.ammo <= 0:
                return projectiles

            num_bullets = 3
            spread_angle = 5
            for i in range(num_bullets):
                angle = (-spread_angle / 2) + i * (
                            spread_angle / (num_bullets - 1))
                rad = math.radians(angle)
                direction = (math.sin(rad), -math.cos(rad))
                projectiles.append(
                    Projectile(pos, (0, 255, 255), direction=direction,
                               speed=12, damage=1))
            if not unlimited_ammo:
                self.ammo -= num_bullets

        return projectiles

    def super_charge(self, joysticks, score, explosions, entities,
                             frame_explode, frame_big_explode):
        if self.charges <= 0:
            return

        if joysticks:
            joysticks[0].rumble(0.5, 1.0, 1000)
        explosions.add(Explosion(self.hitbox.centerx, self.hitbox.centery, frame_big_explode))

        for entity in entities:
            entity.kill()
            explosions.add(Explosion(entity.rect.centerx, entity.rect.centery, frame_explode))
            score += self.level * 10

        if not unlimited_ammo:
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
        self.xp_to_next_level = int(self.xp_to_next_level * self.xp_growth)
        sound[3].play()

    def get_stats(self):
        return {
            "level": self.level,
            "perk_points": self.perk_points,
            "damage": self.damage,
            "crit_chance": self.crit_chance,
            "crit_multiplier": self.crit_multiplier,
            "velocity": self.velocity,
        }