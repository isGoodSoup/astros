from typing import override
from scripts.ability import Ability

class Explorer(Ability):
    @override
    def apply(self, ship, level):
        ship.hitpoints += ship.hitpoints * (level * 0.2)
        ship.shield += ship.shield * (level * 0.2)
        return [ship.hitpoints, ship.shield]

class DamageBoost(Ability):
    @override
    def apply(self, ship, level):
        ship.damage += ship.damage * (level * 0.2)
        return [ship.damage]

class Survival(Ability):
    @override
    def apply(self, ship, level):
        ship.shield = ship.base_shield * (1 + 0.2 * level)
        ship.evasion += 0.01 * level
        return [ship.shield]

class Tank(Ability):
    @override
    def apply(self, ship, level):
        ship.hitpoints = ship.hitpoints * (1 + 0.5 * level)
        return [ship.hitpoints]