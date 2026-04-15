import random

import pygame

from scripts.entity import Entity
from scripts.levels import (DIFFICULTY_ENEMY_SETTINGS)
from scripts.shockwave import Shockwave

__all__ = ['Alien', 'HeavyAlien', 'BomberAlien']

class Alien(Entity):
    def __init__(self, color, x, y, ship, game,
                 base_hp=100, base_damage=10, base_speed=2):
        image_path = f"assets/aliens/{color}.png"
        image = pygame.image.load(image_path).convert_alpha()
        super().__init__(image, x, y)
        self.ship = ship
        self.game = game
        self.color = color
        self.base_hp = base_hp
        self.base_damage = base_damage
        self.base_speed = base_speed
        self.is_elite = self._roll_elite()
        
        # Formation / Movement state
        self.formation_offset = (0, 0)
        self.formation_center = pygame.Vector2(x, y)
        self.in_formation = True
        self.aggro = False
        self.aggro_distance = 400
        
        self._apply_difficulty()

    def _get_scalers(self):
        return DIFFICULTY_ENEMY_SETTINGS[self.game.state.difficulty]

    def _apply_difficulty(self):
        settings = self._get_scalers()

        hp = self.base_hp * settings["hp_multiplier"]
        dmg = self.base_damage * settings["damage_multiplier"]
        spd = self.base_speed * settings["speed_multiplier"]

        fire_rate = settings["fire_rate_multiplier"]

        if self.is_elite:
            hp *= 2.0
            dmg *= 2.0
            spd *= 1.25
            fire_rate *= 1.5

        self.hitpoints = int(hp)
        self.damage = int(dmg)
        self.speed = spd

        self.fire_rate_multiplier = fire_rate
        self.elite_chance = settings["elite_chance"]

    def _roll_elite(self):
        settings = self._get_scalers()
        return random.random() < settings["elite_chance"]

    def force_elite(self):
        self.is_elite = True
        self._apply_difficulty()

    def refresh_difficulty(self):
        self._apply_difficulty()

    def update(self):
        if not self.aggro:
            dist_to_ship = pygame.Vector2(self.rect.center).distance_to(self.ship.rect.center)
            if int(dist_to_ship) < self.aggro_distance:
                self.aggro = True
                self.in_formation = False

        if self.in_formation:
            self.formation_center.y += self.speed
            self.rect.center = self.formation_center + self.formation_offset
            
            if self.rect.top > self.game.screen_size[1]:
                self.kill()
        else:
            target = pygame.Vector2(self.ship.rect.center)
            pos = pygame.Vector2(self.rect.center)
            direction = (target - pos)
            if direction.length() > 0:
                direction = direction.normalize()
                pos += direction * self.speed * 1.5
                self.rect.center = pos

class HeavyAlien(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("yellow", x, y, ship, game, base_hp=200, base_damage=20)

class BomberAlien(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("orange", x, y, ship, game, base_damage=20)
        self.exploded = False
        self.aggro_distance = 500

    def update(self):
        super().update()
        if self.aggro and not self.exploded:
            dist = pygame.Vector2(self.rect.center).distance_to(self.ship.rect.center)
            if dist < 50:
                self.explode()

    def explode(self):
        if not self.exploded:
            self.exploded = True
            self.game.sprites.shockwaves.add(Shockwave(self.rect.center, max_radius=200))
            
            dist = pygame.Vector2(self.rect.center).distance_to(self.ship.rect.center)
            if dist < 200:
                damage_taken = self.ship.damage_taken_multiplier
                total_damage = self.damage * 2 * damage_taken
                if self.ship.shield > 0:
                    self.ship.shield -= total_damage
                else:
                    self.ship.hitpoints -= total_damage
                self.ship.hit = True
                self.ship.last_hit_time = pygame.time.get_ticks()
            
            self.kill()

    def kill(self):
        if not self.exploded:
            self.explode()
        else:
            super().kill()