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
        self.current_phase = self.phases[0]
        self.phase_index = 0
        self.phase_start_time = pygame.time.get_ticks()
        self.phase_to_sprite = {self.phases[i]: i for i in range(self.total_phases)}
        self.phase_colors = ['red', 'green', 'yellow']
        self.phase_length = 30_000
        self.phase_ending = False
        self.phase_spawned = False
        self.current_phase_options = []