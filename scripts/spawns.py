import random

from scripts.settings import UPGRADE_SPAWN_INTERVAL, CELESTIAL_SPAWN_INTERVAL, \
    ALIEN_SPAWN_INTERVAL_RANGE, BLACK_HOLE_SPAWN


class SpawnManager:
    def __init__(self):
        self.celestial_spawn_interval = random.randint(
            *CELESTIAL_SPAWN_INTERVAL)
        self.last_upgrade = None
        self.last_celestial_spawn = 0
        self.last_alien_spawn = 0
        self.last_reinforcement_spawn = 0
        self.last_asteroid_spawn = 0
        self.last_upgrade_spawn = 0
        self.alien_spawn_interval = random.randint(*ALIEN_SPAWN_INTERVAL_RANGE)

        self.last_shot_time = 0
        self.active_upgrade = None
        self.upgrade_spawn_interval = UPGRADE_SPAWN_INTERVAL
        self.upgrade_start_time = 0

        self.boss_spawned = False
        self.boss_alive = False
        self.boss_count = 1
        self.can_spawn_asteroids = True

        self.last_hole_spawn = 0
        self.black_hole_spawn_delay = BLACK_HOLE_SPAWN