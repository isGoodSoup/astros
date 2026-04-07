import pygame

from scripts.shared import joysticks

class Input:
    def __init__(self, screen_size):
        self.left_joystick = [0.0, 0.0]
        self.right_joystick = [0.0, 0.0]
        self.deadzone = 0.2

        self.cursor_pos = [screen_size[0] // 2, screen_size[1] // 2]
        self.cursor_speed = 1000
        self.selected_skill = None
        self.nav_cooldown = 150
        self.last_nav_time = 0
        self.mode = "mouse"
        self.last_input_time = pygame.time.get_ticks()

        self.charge_active = False
        self.charge_start_time = 0
        self.charge_duration = 2000
        self.charge_rumble = 0.3

        self.cursor_visible = False
        self.last_cursor_pos = pygame.mouse.get_pos()
        self.last_move_time = pygame.time.get_ticks()
        self.cursor_hide_delay = 3000

    def update(self, events):
        self.last_input_time = pygame.time.get_ticks()
        for event in events:
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP):
                self.mode = "mouse"
                self.cursor_pos = list(pygame.mouse.get_pos())
            elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN,
                                pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
                self.mode = "controller"

        self.cursor_visible = (pygame.time.get_ticks() -
            self.last_move_time <= self.cursor_hide_delay)

    def act(self, game):
        now = pygame.time.get_ticks()
        shooting_input = (joysticks and joysticks[0].get_button(0)) or \
                         pygame.key.get_pressed()[pygame.K_SPACE]
        if shooting_input:
            if now - game.last_shot_time >= game.ship.shot_cooldown:
                new_projectiles = game.ship.shoot(gun_type=game.ship.gun)
                game.projectiles.add(*new_projectiles)
                game.last_shot_time = now
                if game.play_sound:
                    game.sounds[0].play()
                if game.ship.gun == "shotgun":
                    game.screen_shake = 20

        if joysticks and joysticks[0].get_button(4) and joysticks[0].get_button(5):
            if not self.charge_active and game.ship.charges > 0:
                self.charge_active = True
                self.charge_start_time = now

        pause_input = (joysticks and joysticks[0].get_button(7)) or \
                      pygame.key.get_pressed()[pygame.K_ESCAPE]
        if pause_input and not game.skill_tab.active:
            game.state.pause = not game.state.pause

        if game.skill_tab.active and game.state.current_phase_options and self.mode == "mouse":
            mouse_rect = pygame.Rect(self.cursor_pos[0], self.cursor_pos[1], 1, 1)
            clicked_skill = None
            for skill in game.state.current_phase_options:
                skill_rect = pygame.Rect(skill.pos[0], skill.pos[1],
                                         skill.rect.width, skill.rect.height)
                if skill_rect.colliderect(mouse_rect):
                    clicked_skill = skill
                    break
            if clicked_skill:
                game.skills.unlock_or_upgrade(clicked_skill, game.ship)
                game.skill_tab.close()
                game.state.current_phase_options = []
                game.state.phase_ending = False
                game.state.pause = False