import random

import pygame

from scripts.entity import Entity
from scripts.levels import (DIFFICULTY_ENEMY_SETTINGS)

__all__ = ['Alien']

class Alien(Entity):
    def __init__(self, color, x, y, ship, game,
                 base_hp=100, base_damage=10, base_speed=2):
        image = pygame.image.load(f"assets/aliens/{color}.png").convert_alpha()
        super().__init__(image, x, y)
        self.ship = ship
        self.game = game
        self.base_hp = base_hp
        self.base_damage = base_damage
        self.base_speed = base_speed
        self.is_elite = self._roll_elite()
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