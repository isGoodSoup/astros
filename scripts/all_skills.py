from typing import override

import pygame

from scripts.ability import Ability

class Explorer(Ability):
    @override
    def apply(self, ship, level):
        ship.max_hitpoints += ship.max_hitpoints * (level * 0.2)
        ship.hitpoints = ship.max_hitpoints
        ship.max_shield += ship.max_shield * (level * 0.2)
        ship.shield = ship.max_shield
        return [ship.hitpoints, ship.shield]

class DamageBoost(Ability):
    @override
    def apply(self, ship, level):
        ship.damage += ship.damage * (level * 0.2)
        return [ship.damage]

class Maniac(Ability):
    @override
    def apply(self, ship, level):
        boost = 0.02 * level
        current_time = pygame.time.get_ticks()
        ship.maniac_boost += boost
        ship.maniac_boost_end = current_time + 5000
        return [ship.maniac_boost]

class Madness(Ability):
    @override
    def apply(self, ship, level):
        ship.crit_multiplier += ship.crit_multiplier * (level * 0.2)
        return [ship.crit_multiplier]

class Survival(Ability):
    @override
    def apply(self, ship, level):
        ship.max_shield += ship.max_shield * (0.2 * level)
        ship.shield = ship.max_shield
        ship.evasion += 0.01 * level
        return [ship.shield]

class Adventurer(Ability):
    @override
    def apply(self, ship, level):
        ship.evasion += 0.02 * level
        ship.speed += 0.05 * level * ship.base_speed
        return [ship.evasion, ship.speed]

class Pilot(Ability):
    @override
    def apply(self, ship, level):
        ship.evasion += 0.03 * level
        ship.max_hitpoints += ship.max_hitpoints * (level * 0.2)
        ship.hitpoints = ship.max_hitpoints
        return [ship.hitpoints]

class Tank(Ability):
    @override
    def apply(self, ship, level):
        ship.max_hitpoints += ship.max_hitpoints * (level * 0.7)
        ship.hitpoints = ship.max_hitpoints
        return [ship.hitpoints]