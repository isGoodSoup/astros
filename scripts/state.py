import pygame

from scripts.settings import (PHASES_TOTAL, PHASE_START, PHASE_COLORS, \
                              PHASE_LENGTH, STAR_SPEED,
                              PHASES, SCORE_SCALING, PHASE_ACTIVE, PHASE_FADE)


class GameState:
    def __init__(self):
        self.can_screen_shake = False
        self.can_rumble = True
        self.can_show_controls = True
        self.can_show_hud = True
        self.current_lang = 'en'

        self.score = 0
        self.score_scaling = SCORE_SCALING
        self.score_multiplier = 1.0
        self.high_score = 0
        self.survival_bonus = 0

        self.game_over = False
        self.pause = False
        self.debugging = False
        self.play_sound = True

        self.total_phases = PHASES_TOTAL
        self.phases = PHASES
        self.phase_state = PHASE_ACTIVE
        self.phase_index = PHASE_START
        self.real_phase_index = self.phase_index
        self.current_phase = self.phases[self.phase_index]
        self.current_phase_options = []
        self.phase_start_time = pygame.time.get_ticks()
        self.phase_fade = PHASE_FADE
        self.phase_colors = PHASE_COLORS
        self.phase_length = PHASE_LENGTH
        self.phase_start = True
        self.phase_spawned = False
        self.transition_started = False

        self.game_over_fx = True
        self.skills_generated = False

        self.stars_speed = STAR_SPEED