from typing import override

from scripts.engine.ability import Ability

class Classic(Ability):
    def apply_on(self, game, ship):
        pass

class DoubleTrouble(Ability):
    @override
    def apply_on(self, game, ship):
        game.spawns.boss_count += 1
        game.spawns.can_spawn_asteroids = False
        return [game.spawns.boss_count,
                game.spawns.can_spawn_asteroids]

class GlassReactor(Ability):
    @override
    def apply_on(self, game, ship):
        ship.max_hitpoints *= 0.5
        ship.hitpoints = ship.max_hitpoints
        ship.base_damage *= 2.0
        ship.max_shield = 0
        ship.shield = ship.max_shield
        return [ship.hitpoints, ship.base_damage,ship.shield]

class Commando(Ability):
    def apply_on(self, game, ship):
        ship.is_commando_active = True
        ship.can_overheat = False
        return [ship.is_commando_active, ship.can_overheat]

class Panonium(Ability):
    def apply_on(self, game, ship):
        sp = game.spawns
        sp.boss_count += 1
        sp.can_spawn_elites = True
        sp.shuffle_enemies = True
        sp.alien_spawn_interval = int(sp.alien_spawn_interval * 0.75)
        sp.elite_mutation_chance += 0.25
        sp.can_spawn_asteroids = True
        ship.damage *= 1.10
        return [sp.boss_count, sp.alien_spawn_interval,
                sp.elite_mutation_chance]