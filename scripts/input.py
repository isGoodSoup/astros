import pygame

from scripts.game_over import reboot
from scripts.lang import rotate_language
from scripts.settings import (ONE_SECOND, SCREEN_SHAKE, INPUT_NAV_COOLDOWN,
                              PHASE_TRANSITION, INPUT_MOUSE, INPUT_CONTROLLER,
                              BASE_RUMBLE_MS)
from scripts.shared import joysticks, controller
from scripts.ship import get_nearest_enemy
from scripts.soundlib import decrease_volume, increase_volume
from scripts.utils import take_screenshot


class Input:
    def __init__(self, screen_size):
        self.left_joystick = [0.0, 0.0]
        self.right_joystick = [0.0, 0.0]
        self.deadzone = 0.2

        self.cursor_pos = [screen_size[0] // 2, screen_size[1] // 2]
        self.cursor_speed = ONE_SECOND
        self.selected_skill_index = 0
        self.selected_skill = None
        self.nav_cooldown = INPUT_NAV_COOLDOWN
        self.last_nav_time = 0
        self.mode = INPUT_MOUSE
        self.last_input_time = pygame.time.get_ticks()

        self.cursor_visible = False
        self.last_cursor_pos = pygame.mouse.get_pos()
        self.last_move_time = pygame.time.get_ticks()
        self.cursor_hide_delay = ONE_SECOND * 3
        self.moving_hud = False

    def update(self, game, events):
        now = pygame.time.get_ticks()
        self.last_input_time = pygame.time.get_ticks()
        moved = False

        for event in events:
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP):
                self.mode = INPUT_MOUSE
                self.cursor_pos = list(pygame.mouse.get_pos())
                self.last_move_time = pygame.time.get_ticks()
                moved = True

            elif event.type in (pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN,
                                pygame.JOYBUTTONUP, pygame.JOYHATMOTION):
                self.mode = INPUT_CONTROLLER
                self.last_move_time = pygame.time.get_ticks()

        if moved:
            self.last_move_time = now
            self.cursor_visible = True

        elif game.hud.skill_tab.active:
            self.cursor_visible = False

        elif game.state.current_phase == game.state.phases[-1]:
            self.cursor_visible = False

        else:
            self.cursor_visible = (now - self.last_move_time <= self.cursor_hide_delay)

    def act(self, game, events):
        self.moving_hud = False
        adjusting_hud = False
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()

        is_boss_phase = game.state.current_phase == game.state.phases[-1]

        controller_shoot = False
        if joysticks:
            controller_shoot = (controller.get_button(5)
                                or controller.get_button(0))

        shooting_input = ((controller_shoot or keys[pygame.K_SPACE] or mouse[0])
                          and not game.state.pause)
        if ((shooting_input and now - game.spawns.last_shot_time >=
                game.ship.shot_cooldown) and game.ship.can_shoot()):
            if is_boss_phase:
                enemies = list(game.sprites.bosses)
                target = get_nearest_enemy((game.ship.rect.x, game.ship.rect.y), enemies) \
                    if enemies else None
            else:
                target = None
            if joysticks:
                controller.rumble(1, 2, BASE_RUMBLE_MS + 30)
            new_projectiles = game.ship.shoot(gun_type=game.ship.gun,
                                              target=target)
            game.sprites.projectiles.add(*new_projectiles)
            game.spawns.last_shot_time = now

            if game.ship.guns_ammo[game.ship.gun] <= 0 and game.ship.gun != "beam":
                game.mixer.sounds[4].play()

            if game.state.play_sound:
                game.mixer.sounds[0].play()

            if game.ship.gun == "shotgun" and game.ship.guns_ammo['shotgun'] > 0:
                game.screen_shake = SCREEN_SHAKE // 2

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    rotate_language()
                    game.mixer.sounds[4].play()

                if event.key == pygame.K_TAB:
                    if not game.hud.skill_tab.active:
                        if game.hud.stats_tab.active:
                            game.hud.stats_tab.close()
                        else:
                            game.hud.stats_tab.open((game.screen_size[0] // 2 -
                                                     game.hud.stats_tab.rect.width // 2,
                                                     game.screen_size[1] // 2))
                    else:
                        game.hud.skill_tab.close()

                if game.hud.skill_tab.active:
                    num_skills = len(game.state.current_phase_options)
                    if event.key == pygame.K_LEFT:
                        self.selected_skill_index = ((self.selected_skill_index - 1) % num_skills)
                    elif event.key == pygame.K_RIGHT:
                        self.selected_skill_index = ((self.selected_skill_index + 1) % num_skills)

                    if (event.key == pygame.K_RETURN and
                            game.hud.skill_tab.active and
                            game.state.current_phase_options):

                        selected = (game.state.current_phase_options
                        [self.selected_skill_index])

                        game.skills.unlock_or_upgrade(selected, game.ship)

                        if selected.unlocked and selected not in game.ship.skills:
                            game.ship.add_skill(selected)

                        game.hud.skill_tab.close()
                        game.state.current_phase_options = []
                        game.state.pause = False

                if event.key == pygame.K_g:
                    game.ship.switch_gun()

                if event.key == pygame.K_r and game.state.game_over:
                    reboot(game, game.screen_size)

                if event.key == pygame.K_l:
                    from scripts.movement import lock_y
                    lock_y = not lock_y

                if event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    increase_volume(game)

                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    decrease_volume(game)

                if event.key == pygame.K_F2:
                    game.state.debugging = not game.state.debugging

                if event.key == pygame.K_F5:
                    game.font.update()

                if event.key == pygame.K_F12:
                    take_screenshot(game)

                if event.key == pygame.K_ESCAPE:
                    if not game.hud.skill_tab.active:
                        game.state.pause = not game.state.pause

                if event.key == pygame.K_q:
                    if event.mod & pygame.KMOD_CTRL:
                        if game.state.pause and not game.hud.skill_tab.active:
                            game.running = False

            elif event.type == pygame.JOYBUTTONDOWN:
                if (event.button == 0 and
                        game.hud.skill_tab.active and
                        game.state.current_phase_options):

                    selected = (game.state.current_phase_options
                    [self.selected_skill_index])

                    game.skills.unlock_or_upgrade(selected, game.ship)

                    if selected.unlocked and selected not in game.ship.skills:
                        game.ship.add_skill(selected)

                    game.hud.skill_tab.close()
                    game.state.current_phase_options = []
                    game.state.pause = False

                if event.button == 1:
                    if not game.hud.skill_tab.active:
                        if game.hud.stats_tab.active:
                            game.hud.stats_tab.close()
                        else:
                            game.hud.stats_tab.open((game.screen_size[0] // 2 -
                                                     game.hud.stats_tab.rect.width // 2,
                                                     game.screen_size[1] // 2))
                    else:
                        game.hud.skill_tab.close()

                if event.button == 2:
                    game.ship.switch_gun()

                if event.button == 3 and game.state.game_over:
                    reboot(game, game.screen_size)

                if event.button == 4:
                    from scripts.movement import lock_y
                    lock_y = not lock_y

                if event.button == 6:
                    if game.state.pause and not game.hud.skill_tab.active:
                        game.running = False

                if event.button == 7:
                    if not game.hud.skill_tab.active:
                        game.state.pause = not game.state.pause


            elif event.type == pygame.JOYHATMOTION:
                if game.hud.skill_tab.active and game.state.current_phase_options:
                    now = pygame.time.get_ticks()

                    if now - self.last_nav_time > self.nav_cooldown:
                        dx, dy = event.value
                        num_skills = len(game.state.current_phase_options)

                        if dx == -1:
                            self.selected_skill_index = ((self.selected_skill_index - 1)
                                                         % num_skills)
                        elif dx == 1:
                            self.selected_skill_index = ((self.selected_skill_index + 1)
                                                         % num_skills)

                        self.selected_skill = (game.state.current_phase_options
                            [self.selected_skill_index])
                        self.last_nav_time = now
                else:
                    if event.hat == 0 and event.value == (-1, 0):
                        game.font.update()

                    if event.hat == 0 and event.value == (1, 0):
                        take_screenshot(game)

        axis_y = 0.0
        if joysticks and controller.get_button(9):
            axis_y = controller.get_axis(3)
            if abs(axis_y) < game.input.deadzone:
                axis_y = 0.0

        hud_padding_increase = (axis_y < -0.2) or keys[pygame.K_F4]
        hud_padding_decrease = (axis_y > 0.2) or keys[pygame.K_F3]

        try:
            if hud_padding_increase:
                game.hud_padding += 1
            elif hud_padding_decrease:
                game.hud_padding -= 1
        finally:
            self.moving_hud = True

        if game.hud.skill_tab.active and game.state.current_phase_options and self.mode == INPUT_MOUSE:
            mouse_rect = pygame.Rect(self.cursor_pos[0], self.cursor_pos[1], 1, 1)
            clicked_skill = None

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for skill in game.state.current_phase_options:
                        skill_rect = pygame.Rect(skill.pos[0], skill.pos[1], skill.rect.width,
                                                 skill.rect.height)
                        if skill_rect.colliderect(mouse_rect):
                            clicked_skill = skill
                            break

            if clicked_skill:
                game.skills.unlock_or_upgrade(clicked_skill, game.ship)
                game.hud.skill_tab.close()
                game.state.current_phase_options = []
                game.state.phase_state = PHASE_TRANSITION
                game.state.pause = False

def update_axis(game):
    if joysticks:
        rx = controller.get_axis(2)
        ry = controller.get_axis(3)

        rx = 0 if abs(rx) < game.input.deadzone else rx
        ry = 0 if abs(ry) < game.input.deadzone else ry

        game.input.right_joystick[0] = rx
        game.input.right_joystick[1] = ry

        lx = controller.get_axis(0)
        ly = controller.get_axis(1)
        lx = 0 if abs(lx) < game.input.deadzone else lx
        ly = 0 if abs(ly) < game.input.deadzone else ly
        game.input.left_joystick[0] = lx
        game.input.left_joystick[1] = ly

def update_cursor(game, delta, screen_size):
    update_axis(game)
    rx, ry = game.input.right_joystick
    deadzone = game.input.deadzone

    if abs(rx) > deadzone or abs(ry) > deadzone:
        game.input.cursor_pos[0] += rx * game.input.cursor_speed * delta
        game.input.cursor_pos[1] += ry * game.input.cursor_speed * delta

        game.input.cursor_pos[0] = max(0, min(screen_size[0],
                                              game.input.cursor_pos[0]))
        game.input.cursor_pos[1] = max(0, min(screen_size[1],
                                              game.input.cursor_pos[1]))

        game.input.mode = INPUT_CONTROLLER
        game.input.last_move_time = pygame.time.get_ticks()