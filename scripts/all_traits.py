from typing import override

from scripts.ability import Ability


class DoubleBoss(Ability):
    @override
    def apply_on(self, game, ship):
        game.spawns.boss_count += 1
        game.spawns.can_spawn_asteroids = False
        return [game.state.boss_count, game.state.can_spawn_asteroids]