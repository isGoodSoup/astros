import pygame

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

        self.total_phases = 6
        self.phases = [f"wave_{i+1}" for i in range(self.total_phases)]
        self.phase_index = 0
        self.current_phase = self.phases[self.phase_index]
        self.current_phase_options = []
        self.phase_start_time = pygame.time.get_ticks()
        self.phase_to_sprite = {self.phases[i]: i for i in range(self.total_phases)}
        self.phase_colors = ['red', 'green', 'yellow']
        self.phase_length = 15_000
        self.phase_ending = False
        self.phase_spawned = False

        self.boss_spawned = False
        self.boss_alive = False

        self.game_over_fx = True
        self.skills_generated = False

        self.stars_speed = 2