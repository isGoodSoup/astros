from typing import override

import pygame

from scripts.engine.ability import Ability
from scripts.system.constants import SHIP_MANIC_BOOST

__all__ = ['Explorer', 'DamageBoost', 'Maniac', 'Madness','Survival',
           'Adventurer', 'Pilot', 'Tank', 'Tower', 'Fortified',
           'BrushOfDeath']

class Explorer(Ability):
    @override
    def apply(self, ship, level):
        ship.max_hitpoints += ship.max_hitpoints * 0.1
        ship.hitpoints = ship.max_hitpoints
        ship.max_shield += ship.max_shield * 0.1
        ship.shield = ship.max_shield
        ship.velocity *= (1 - 0.02)
        return [ship.hitpoints, ship.shield, ship.velocity]

class DamageBoost(Ability):
    @override
    def apply(self, ship, level):
        ship.damage += 0.2
        ship.max_hitpoints *= 0.95
        ship.hitpoints = min(ship.hitpoints, ship.max_hitpoints)
        ship.max_shield *= 0.95
        ship.shield = min(ship.shield, ship.max_shield)
        return [ship.damage]

class Maniac(Ability):
    @override
    def apply(self, ship, level):
        boost = 0.02 * level
        current_time = pygame.time.get_ticks()
        ship.maniac_boost += boost
        ship.maniac_boost_end = current_time + SHIP_MANIC_BOOST
        ship.maniac_penalty = 0.10 * level
        return [ship.maniac_boost]

class Madness(Ability):
    @override
    def apply(self, ship, level):
        ship.crit_multiplier += 0.2
        ship.evasion -= 0.02
        return [ship.crit_multiplier, ship.evasion]

class Survival(Ability):
    @override
    def apply(self, ship, level):
        ship.max_shield += ship.max_shield * 0.1
        ship.shield = ship.max_shield
        ship.evasion += 0.01
        ship.damage *= 0.95
        return [ship.shield, ship.evasion, ship.damage]

class Adventurer(Ability):
    @override
    def apply(self, ship, level):
        ship.evasion += 0.02
        ship.velocity += 0.05
        ship.max_shield *= 0.95
        ship.shield = min(ship.shield, ship.max_shield)
        return [ship.evasion, ship.velocity, ship.shield]

class Pilot(Ability):
    @override
    def apply(self, ship, level):
        ship.evasion += 0.02
        ship.max_hitpoints += ship.max_hitpoints * 0.2
        ship.hitpoints = ship.max_hitpoints
        ship.damage *= 0.95
        return [ship.hitpoints, ship.evasion, ship.damage]

class Tank(Ability):
    @override
    def apply(self, ship, level):
        ship.max_hitpoints += ship.max_hitpoints * 0.7
        ship.hitpoints = ship.max_hitpoints
        ship.velocity *= 0.9
        ship.evasion -= 0.03
        return [ship.hitpoints, ship.velocity, ship.evasion]

class Tower(Ability):
    @override
    def apply(self, ship, level):
        ship.velocity *= (1 - 0.05 * level)
        boost_amount = int(ship.base_max_shield * 1.5 * level)
        if not ship.moving and not ship.tower_boost_applied:
            ship.tower_boost = boost_amount
            ship.shield += boost_amount
            ship.tower_boost_applied = True
        elif ship.moving and ship.tower_boost_applied:
            ship.shield -= ship.tower_boost
            ship.tower_boost = 0
            ship.tower_boost_applied = False
        return [ship.shield, ship.velocity]

class Fortified(Ability):
    @override
    def apply(self, ship, level):
        ship.fortified_percent = 0.1 * level
        ship.fortified_cap = 50 * level
        ship.shield_regen_multiplier = getattr(ship, "shield_regen_multiplier", 1.0)
        ship.shield_regen_multiplier *= (1 - 0.05 * level)
        return [ship.fortified_percent, ship.fortified_cap]

class BrushOfDeath(Ability):
    @override
    def apply(self, ship, level):
        ship.can_use_bod = True
        return [ship.can_use_bod]