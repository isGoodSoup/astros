import math
import random

import pygame

from scripts.proj import Projectile
from scripts.toggles import unlimited_ammo


class Ship(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, x, y, frame, width, height, scale=4,
                 columns=1):
        super().__init__()
        self.original_image = sprite_sheet.get_image(frame, width, height,scale, columns)
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6, self.rect.height * -0.6)
        self.current_angle = 90
        self.velocity = 12
        self.direction = "idle"
        self.shooting = False
        self.moving = False
        self.max_hitpoints = 200
        self.hitpoints = self.max_hitpoints
        self.max_shield = 25
        self.base_max_shield = self.max_shield
        self.shield = self.max_shield
        self.gun_order = ['beam', 'shotgun', 'auto', 'missile']
        self.gun = "beam"
        self.guns = {"beam": 250, "shotgun": 400, "auto": 150, "missile": 900}
        self.guns_ammo = {"beam": -1, "shotgun": 20, "auto": 400, "missile": 10}
        self.base_guns_ammo = self.guns_ammo.copy()
        self.arsenal = sum(self.guns_ammo.values())
        self.base_damage = 4
        self.damage = self.base_damage
        self.combo_multiplier = 1.0
        self.powerup_multiplier = 1.0
        self.base_crit_chance = 0.05
        self.crit_chance = self.base_crit_chance
        self.crit_multiplier = 3

        self.base_charges = 1
        self.charges = self.base_charges
        self.evasion = 0.02
        self.shot_cooldown = 250
        self.power_ups = []

        self.maniac_boost = 0
        self.maniac_boost_end = 0

        self.tower_boost = 0
        self.tower_boost_end = 0
        self.tower_boost_applied = False

        self.fortified_percent = 0
        self.fortified_cap = 200

        self.skills = []

        self.level = 1
        self.level_cap = False
        self.xp = 0
        self.xp_to_next_level = 256
        self.perk_points = 0
        self.xp_growth = 2.0
        self.credits = 0

        self.hit = False
        self.critical = False

        self.shield_regen = False
        self.shield_regen_end = 0
        self.shield_regen_rate = int(self.max_shield * 0.05)

        self.last_hit_time = 0
        self.hit_cooldown = 200

    def add_skill(self, skill):
        self.skills.append(skill)

    def update_upgrades(self):
        now = pygame.time.get_ticks()

        self.power_ups = [end for end in getattr(self, "power_ups", []) if
                          end > now]
        if self.power_ups:
            self.powerup_multiplier = 2 ** len(self.power_ups)
        else:
            self.powerup_multiplier = 1.0

        if getattr(self, "shield_regen", False):
            if now < self.shield_regen_end:
                self.shield += self.shield_regen_rate / 60
                self.shield = min(self.shield, self.max_shield)
            else:
                self.shield_regen = False

    def update_damage(self):
        self.damage = self.base_damage

        if self.gun == "shotgun":
            self.damage *= 10
        elif self.gun == "missile":
            self.damage *= 50

    def update_fire_rate(self):
        self.shot_cooldown = self.guns[self.gun]

    def update_position(self, x, y):
        self.rect.topleft = (x, y)
        self.hitbox.center = self.rect.center

    def switch_gun(self):
        idx = self.gun_order.index(self.gun)
        self.gun = self.gun_order[(idx + 1) % len(self.gun_order)]
        self.update_fire_rate()

    def rotate_to(self, target_angle, smooth=True):
        if smooth:
            angle_diff = (target_angle - self.current_angle + 180) % 360 - 180
            self.current_angle += angle_diff * 0.3
        else:
            self.current_angle = target_angle
        self.image = pygame.transform.rotate(self.original_image,
                                             -self.current_angle)

    def shoot(self, gun_type=None, target=None):
        self.update_damage()
        if gun_type is None:
            gun_type = self.gun

        pos = self.hitbox.center

        if target:
            direction_vec = aim_at_target(pos, target)
            dir_x, dir_y = direction_vec.x, direction_vec.y
        else:
            rad = math.radians(self.current_angle)
            dir_x = math.cos(rad)
            dir_y = -math.sin(rad)

        projectiles = []

        if gun_type == "beam":
            projectiles.append(Projectile(pos, (0, 255, 255), direction=(dir_x, dir_y),
                           speed=16,
                           damage=1))

        elif gun_type == "shotgun":
            if self.guns_ammo['shotgun'] <= 0:
                return projectiles
            num_pellets = 6
            spread_angle = 30

            for i in range(num_pellets):
                angle_offset = (-spread_angle / 2) + i * (
                        spread_angle / (num_pellets - 1))
                if target:
                    angle_rad = math.atan2(-dir_y, dir_x) + math.radians(
                        angle_offset)
                    direction = (math.cos(angle_rad), -math.sin(angle_rad))
                else:
                    rad = math.radians(self.current_angle + angle_offset)
                    direction = (math.cos(rad), -math.sin(rad))
                projectiles.append(
                    Projectile(pos, (0, 255, 255), direction=direction,
                               speed=12, damage=self.damage))
            if not unlimited_ammo:
                self.guns_ammo['shotgun'] -= max(0, num_pellets)

        if gun_type == "auto":
            if self.guns_ammo['auto'] <= 0:
                return projectiles

            num_bullets = 3
            spread_angle = 5
            for i in range(num_bullets):
                angle_offset = (-spread_angle / 2) + i * (
                        spread_angle / (num_bullets - 1))
                if target:
                    angle_rad = math.atan2(-dir_y, dir_x) + math.radians(
                        angle_offset)
                    direction = (math.cos(angle_rad), -math.sin(angle_rad))
                else:
                    rad = math.radians(self.current_angle + angle_offset)
                    direction = (math.cos(rad), -math.sin(rad))
                projectiles.append(
                    Projectile(pos, (0, 255, 255), direction=direction,
                               speed=12, damage=self.damage))

            if not unlimited_ammo:
                self.guns_ammo['auto'] -= max(0, num_bullets)

        if gun_type == "missile":
            if self.guns_ammo['missile'] <= 0:
                return projectiles

            projectiles.append(Projectile(pos,(255, 50, 0),
                    direction=(dir_x, dir_y), speed=4,damage=0))
            projectiles[-1].nuke = True

        return projectiles

    def taken_damage(self):
        return [random.randint(0,10) - 4, random.randint(0,10) - 4]

    def gain_xp(self, amount, sound):
        if self.level_cap and self.level == 10:
            return

        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up(sound)

    def level_up(self, sound):
        if self.level_cap and self.level == 10:
            return

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

def get_nearest_enemy(ship_pos, enemies):
    closest = None
    min_dist = float('inf')
    for enemy in enemies:
        ex, ey = enemy.rect.center
        dx = ex - ship_pos[0]
        dy = ey - ship_pos[1]
        dist_sq = dx*dx + dy*dy
        if dist_sq < min_dist:
            min_dist = dist_sq
            closest = enemy
    return closest

def aim_at_target(ship_pos, target):
    if not target:
        return pygame.Vector2(1, 0)
    ex, ey = target.rect.center
    dx = ex - ship_pos[0]
    dy = ey - ship_pos[1]
    direction = pygame.Vector2(dx, dy)
    if direction.length() != 0:
        direction = direction.normalize()
    return direction