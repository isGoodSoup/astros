import pygame

from scripts.settings import (PHASES_TOTAL, PHASE_START, PHASE_COLORS, \
                              PHASE_LENGTH, BLACK_HOLE_SPAWN, STAR_SPEED,
                              PHASES)

class GameState:
    def __init__(self):
        self.score = 0
        self.score_multiplier = 1.0
        self.high_score = 0
        self.survival_bonus = 0

        self.game_over = False
        self.pause = False
        self.debugging = False
        self.play_sound = True

        self.total_phases = PHASES_TOTAL
        self.phases = PHASES
        self.phase_index = PHASE_START
        self.current_phase = self.phases[self.phase_index]
        self.current_phase_options = []
        self.phase_start_time = pygame.time.get_ticks()
        self.phase_to_sprite = {self.phases[i]: i for i in range(self.total_phases)}
        self.phase_colors = PHASE_COLORS
        self.phase_length = PHASE_LENGTH
        self.phase_ending = False
        self.phase_spawned = False
        self.phase_transitioned = False

        self.boss_spawned = False
        self.boss_alive = False

        self.last_hole_spawn = 0
        self.black_hole_spawn_delay = BLACK_HOLE_SPAWN

        self.game_over_fx = True
        self.skills_generated = False

        self.stars_speed = STAR_SPEED