import math
import random

import pygame

from scripts.proj import Projectile
from scripts.constants import *
from scripts.levels import DIFFICULTY_SHIP_SETTINGS
from scripts.entity import Entity


class Ship(Entity):
    def __init__(self, image, game, x, y):
        super().__init__(image, x, y)
        self.base_image = self.image
        self.game = game
        self.current_angle = SHIP_BASE_ANGLE
        self.velocity = SHIP_VELOCITY
        self.shooting = False
        self.moving = False
        self.max_hitpoints = SHIP_MAX_HITPOINTS
        self.hitpoints = self.max_hitpoints
        self.max_shield = SHIP_MAX_SHIELD
        self.base_max_shield = self.max_shield
        self.shield = self.max_shield
        self.gun_order = SHIP_GUNS
        self.gun = SHIP_GUNS[0]
        self.guns = SHIP_GUNS_RATES
        self.guns_ammo = SHIP_AMMO
        self.base_guns_ammo = self.guns_ammo.copy()

        total_arsenal = 0
        for ammo in self.guns_ammo:
            if ammo == "beam": continue
            total_arsenal += self.guns_ammo[ammo]

        self.arsenal = total_arsenal
        self.base_damage = SHIP_BASE_DAMAGE
        self.damage = self.base_damage
        self.damage_taken_multiplier = 1.0
        self.combo_multiplier = 1.0
        self.powerup_multiplier = 1.0
        self.base_crit_chance = SHIP_BASE_CRIT_CHANCE
        self.crit_chance = self.base_crit_chance
        self.crit_multiplier = 3

        self.can_overheat = True
        self.heat = 0
        self.heat_per_shot = 100
        self.overheat_limit = SHIP_OVERHEAT_CAP
        self.overheated = False
        self.previous_overheat = False
        self.overheat_cooldown = SHIP_OVERHEAT_COOLDOWN
        self.overheat_end_time = 0

        self.evasion = 0.02
        self.shot_cooldown = SHIP_FIRE_RATE
        self.power_ups = []

        self.maniac_boost = 0
        self.maniac_boost_end = 0
        self.maniac_penalty = 0

        self.tower_boost = 0
        self.tower_boost_end = 0
        self.tower_boost_applied = False

        self.fortified_percent = 0
        self.fortified_cap = 200

        self.skills = []

        self.level = 1
        self.level_cap = TOGGLE_LEVEL_CAP
        self.xp = 0
        self.xp_to_next_level = SHIP_XP_PER_LEVEL
        self.perk_points = 0
        self.xp_growth = SHIP_XP_GROWTH
        self.credits = 0
        self.credits_multiplier = 1.0

        self.hit = False
        self.critical = False

        self.shield_regen = False
        self.shield_regen_end = 0
        self.shield_regen_multiplier = 0.05
        self.shield_regen_rate = int(
            self.max_shield * self.shield_regen_multiplier)

        self.is_commando_active = False

        self.last_hit_time = 0
        self.hit_cooldown = SHIP_IFRAMES

        self.apply_difficulty()

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def apply_difficulty(self):
        settings = DIFFICULTY_SHIP_SETTINGS[self.game.state.difficulty]

        self.damage_taken_multiplier = settings["damage_taken_multiplier"]
        self.max_hitpoints = int(self.max_hitpoints * settings["hp_multiplier"])
        self.hitpoints = self.max_hitpoints

        self.max_shield = int(self.max_shield * settings["shield_multiplier"])
        self.base_max_shield = self.max_shield
        self.shield = self.max_shield

        self.base_damage = int(self.base_damage * settings["damage_multiplier"])
        self.crit_chance = self.base_crit_chance + settings["crit_bonus"]
        self.evasion += settings["evasion_bonus"]

        self.shot_cooldown = int(self.shot_cooldown *
                                 settings["cooldown_multiplier"])
        self.heat_per_shot = settings["heat_per_shot"]

        self.shield_regen_multiplier = settings["shield_regen_multiplier"]
        self.shield_regen_rate = int(
            self.max_shield * self.shield_regen_multiplier)

        for gun, ammo in self.guns_ammo.items():
            if gun != "beam":
                scaled_ammo = int(ammo * settings["ammo_multiplier"])
                self.guns_ammo[gun] = scaled_ammo
                self.base_guns_ammo[gun] = scaled_ammo

        self.xp_growth = settings["xp_growth"]
        self.credits_multiplier = settings["credits_multiplier"]

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
                self.shield += self.shield_regen_rate / FPS
                self.shield = min(self.shield, self.max_shield)
            else:
                self.shield_regen = False

    def update_damage(self):
        self.damage = self.base_damage // 2 if self.is_commando_active else (
            self.base_damage)

        if self.gun == "shotgun":
            self.damage *= SHIP_SHOTGUN_DAMAGE // 2 if (
                self.is_commando_active) else SHIP_SHOTGUN_DAMAGE
        elif self.gun == "nuke":
            self.damage *= SHIP_NUKE_DAMAGE // 2 if self.is_commando_active \
                else SHIP_NUKE_DAMAGE

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
            angle_diff = ((target_angle - self.current_angle + 180) % 360 - 180)
            self.current_angle += angle_diff * 0.3
        else:
            self.current_angle = target_angle

        self._apply_rotation()

    def _apply_rotation(self):
        self.image = pygame.transform.rotozoom(
            self.base_image,
            self.current_angle,
            1
        )
        self.rect = self.image.get_rect(center=self.rect.center)
        self.update_hitbox()

    def apply_heat(self, game):
        if not self.can_overheat:
            return

        self.heat += self.heat_per_shot
        if self.heat >= self.overheat_limit:
            self.overheated = True
            self.previous_overheat = self.overheated
            self.overheat_end_time = pygame.time.get_ticks() + self.overheat_cooldown

    def _overheat_cooldown(self, game, delta):
        if not self.overheated:
            self.heat = max(0, self.heat - SHIP_OVERHEAT_RATE * delta)
            if self.heat == 0 and self.previous_overheat:
                game.mixer.play(4)
                self.previous_overheat = False

    def can_shoot(self):
        now = pygame.time.get_ticks()

        if self.overheated:
            if now >= self.overheat_end_time:
                self.overheated = False
                self.heat = 0
            else:
                return False
        return True

    def shoot(self, game, gun_type=None, target=None):
        if not self.can_shoot():
            return []

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
            dir_y = math.sin(rad)

        projectiles = []

        if gun_type == "beam":
            projectiles.append(
                Projectile(pos, COLOR_BLUE, direction=(dir_x, dir_y),
                           speed=24, damage=1))

        elif gun_type == "shotgun":
            num_pellets = SHIP_SHOTGUN_PELLETS
            cost = num_pellets

            if self.guns_ammo['shotgun'] < cost:
                return projectiles

            spread_angle = SHIP_SHOTGUN_SPREAD

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
                    Projectile(pos, COLOR_BLUE, direction=direction,
                               speed=24, damage=self.damage))
            if not TOGGLE_UNLIMITED_AMMO:
                self.guns_ammo['shotgun'] -= cost
                self.clamp_ammo(gun_type)

        if gun_type == "auto":
            num_bullets = SHIP_AUTO_BULLETS
            cost = num_bullets

            if self.guns_ammo['auto'] < cost:
                return projectiles

            spread_angle = SHIP_AUTO_SPREAD
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
                    Projectile(pos, COLOR_BLUE, direction=direction,
                               speed=24, damage=self.damage))

            if not TOGGLE_UNLIMITED_AMMO:
                self.guns_ammo['auto'] -= cost
                self.clamp_ammo(gun_type)

        if gun_type == "nuke":
            cost = 1
            if self.guns_ammo['nuke'] <= cost:
                return projectiles

            projectiles.append(Projectile(pos, COLOR_RED,
                                          direction=(dir_x, dir_y), speed=4,
                                          damage=0))
            projectiles[-1].nuke = True

            if not TOGGLE_UNLIMITED_AMMO:
                self.guns_ammo['nuke'] -= cost
                self.clamp_ammo(gun_type)

        self.apply_heat(game)
        return projectiles

    def clamp_ammo(self, gun):
        self.guns_ammo[gun] = max(0, min(self.guns_ammo[gun],
                                         self.base_guns_ammo[gun]))

    def taken_damage(self):
        return [random.randint(0, 10) - 4, random.randint(0, 10) - 4]

    def gain_xp(self, amount, sound):
        if self.level_cap and self.level == LEVEL_CAP:
            return

        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up(sound)

    def level_up(self, sound):
        if self.level_cap and self.level == LEVEL_CAP:
            return

        self.level += 1
        self.base_damage += 1
        self.max_hitpoints += SHIP_LEVEL_ADDITION
        self.hitpoints = self.max_hitpoints
        self.max_shield += SHIP_LEVEL_ADDITION
        self.shield = self.max_shield
        self.xp_to_next_level = int(self.xp_to_next_level * self.xp_growth)
        self.game.mixer.play(3)

    def get_stats(self):
        return {
            "level": self.level,
            "perk_points": self.perk_points,
            "damage": self.damage,
            "crit_chance": self.crit_chance,
            "crit_multiplier": self.crit_multiplier,
            "velocity": self.velocity,
        }

    def spawnpoint(self, screen_size, frame_width=26):
        x = screen_size[0] // 2 - frame_width // 2
        y = screen_size[1] // 2 + SHIP_OFFSETS[1]
        self.rect.topleft = (x, y)
        self.hitbox.center = self.rect.center


def get_nearest_enemy(ship_pos, enemies):
    closest = None
    min_dist = float('inf')
    for enemy in enemies:
        ex, ey = enemy.rect.center
        dx = ex - ship_pos[0]
        dy = ey - ship_pos[1]
        dist_sq = dx * dx + dy * dy
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
