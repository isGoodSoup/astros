import pygame

from scripts.shared import joysticks, controller
from scripts.soundlib import decrease_volume, increase_volume
from scripts.utils import take_screenshot


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
        self.has_moved = False

    def update(self, events):
        self.last_input_time = pygame.time.get_ticks()
        for event in events:
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP):
                self.mode = "mouse"
                self.has_moved = True
                self.cursor_pos = list(pygame.mouse.get_pos())
                self.last_move_time = pygame.time.get_ticks()

            elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN,
                                pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
                self.mode = "controller"
                self.has_moved = True
                self.last_move_time = pygame.time.get_ticks()

        self.cursor_visible = (self.has_moved and pygame.time.get_ticks() -
                               self.last_move_time <= self.cursor_hide_delay)

    def act(self, game):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        shooting_input = (joysticks and controller.get_button(0)) or keys[
            pygame.K_SPACE]
        if shooting_input:
            if now - game.last_shot_time >= game.ship.shot_cooldown:
                new_projectiles = game.ship.shoot(gun_type=game.ship.gun)
                game.projectiles.add(*new_projectiles)
                game.last_shot_time = now
                
                if game.state.play_sound:
                    game.sounds[0].play()

                if game.ship.gun == "shotgun" and game.ship.ammo > 0:
                    game.screen_shake = 20

        if ((joysticks and controller.get_button(4) and controller.get_button(5))
                or keys[pygame.K_f]):
            if not self.charge_active and game.ship.charges > 0:
                self.charge_active = True
                self.charge_start_time = now

        pause_input = ((joysticks and controller.get_button(7))
                       or keys[pygame.K_ESCAPE])
        if pause_input and not game.hud.skill_tab.active:
            game.state.pause = not game.state.pause

        lock_input = (keys[pygame.K_l]
            or (joysticks and controller.get_button(4)))
        if lock_input:
            from scripts.movement import lock_y
            lock_y = not lock_y

        switch_gun_input = (keys[pygame.K_g]
            or (joysticks and controller.get_button(2)))
        if switch_gun_input:
            game.ship.switch_gun()

        volume_up = keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS] or (
                    joysticks and controller.get_hat(0)[1] == 1)
        volume_down = keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS] or (
                    joysticks and controller.get_hat(0)[1] == -1)
        if volume_up:
            increase_volume(game)
        if volume_down:
            decrease_volume(game)

        hud_padding_increase = keys[pygame.K_F4]
        hud_padding_decrease = keys[pygame.K_F3]

        if hud_padding_increase:
            game.hud_padding += 1
        elif hud_padding_decrease:
            game.hud_padding -= 1

        screenshot_input = keys[pygame.K_F12] or (
                    joysticks and controller.get_hat(0)[0] == 1)
        if screenshot_input:
            take_screenshot(game, game.screen)

        stats_input = keys[pygame.K_TAB] or (joysticks and controller.get_button(1))
        if stats_input and not game.hud.skill_tab.active:
            if game.hud.stats_tab.active:
                game.hud.stats_tab.close()
            else:
                game.hud.stats_tab.open((game.screen_size[0] // 2 - game.hud.stats_tab.rect.width // 2,
                                        game.screen_size[1] // 2))

        if game.hud.skill_tab.active and game.state.current_phase_options and self.mode == "mouse":
            mouse_rect = pygame.Rect(self.cursor_pos[0], self.cursor_pos[1],  1, 1)
            clicked_skill = None
            for skill in game.state.current_phase_options:
                skill_rect = pygame.Rect(skill.pos[0], skill.pos[1],
                                         skill.rect.width, skill.rect.height)
                if skill_rect.colliderect(mouse_rect):
                    clicked_skill = skill
                    break
            if clicked_skill:
                game.skills.unlock_or_upgrade(clicked_skill, game.ship)
                game.hud.skill_tab.close()
                game.state.current_phase_options = []
                game.state.phase_ending = False
                game.state.pause = False