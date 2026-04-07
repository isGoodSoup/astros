import datetime
import json
import os

import pygame as pg
from pygame.constants import *

from scripts import movement
from scripts.celestial import *
from scripts.clock import update_time
from scripts.controller import update_controller
from scripts.credits import update_credits
from scripts.game_over import reboot, game_lost
from scripts.hud import Interface
from scripts.movement import update_movement
from scripts.render import render_stats_tab, render_skills_tab, render_frame
from scripts.shared import joysticks, controller, fade
from scripts.sheet import SpriteSheet
from scripts.ship import Ship
from scripts.skill import SkillManager
from scripts.skill_tab import Tab
from scripts.soundlib import load_sounds, load_ost, increase_volume, \
    decrease_volume, apply_volume
from scripts.toggles import tutorial_on
from scripts.tutorial import Tutorial
from scripts.update import set_hud, update_game, update_hud
from scripts.utils import debug, apply_curve, hide_cursor


# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.
# All assets in this game are © 2026 Diego. See ASSETS_LICENSE.txt.

class Game:
    def __init__(self, screen, screen_size, hud_ratio,
                 game_font):
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, ".saves")
        os.makedirs(save_dir, exist_ok=True)
        self.config_path = os.path.join(save_dir, "config.json")

        self.fps = 60
        self.frame = 0
        self.screen_size = screen_size
        self.prev_state = None
        self.scale = 4
        self.sounds = load_sounds()
        self.theme = load_ost()
        self.volume = 0.5

        self.total_phases = 6
        self.phases = [f"wave_{i+1}" for i in range(self.total_phases)]
        self.current_phase = self.phases[0]
        self.phase_index = 0
        self.phase_to_sprite = {self.phases[i] : i for i in range(self.total_phases)}
        self.phase_colors = ['red', 'green', 'yellow']
        self.current_phase_options = []
        self.phase_start_time = pg.time.get_ticks()
        self.phase_length = 30_000
        self.phase_ending = False
        self.phase_spawned = False

        self.boss_alive = False

        self.celestials = pg.sprite.Group()
        self.projectiles = pg.sprite.Group()
        self.enemy_projectiles = pg.sprite.Group()
        self.aliens = pg.sprite.Group()
        self.bosses = pg.sprite.Group()
        self.asteroids = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.upgrades = pg.sprite.Group()
        self.floating_numbers = pg.sprite.Group()
        self.entities = pg.sprite.Group()
        self.fleets = []
        self.particles = []
        self.stars_speed = 2

        self.cols = 9
        self.explosion_frames = 7
        self.destroy_all = False
        self.ship_sprite = [SpriteSheet("assets/ship.png"), SpriteSheet(
            "assets/ship_v2.png"), SpriteSheet("assets/ship_v3.png")]
        self.explosion_sheet = SpriteSheet("assets/explosion.png")
        self.megaexplosion_sheet = SpriteSheet("assets/explosion_charge.png")
        framew = self.ship_sprite[0].sheet.get_width() // self.cols
        frameh = self.ship_sprite[0].sheet.get_height()
        self.ship = Ship(self.ship_sprite[0], 0, 0, self.frame, framew, frameh, columns=self.cols)
        self.spawnpoint(self.ship, screen_size, self.ship_sprite, self.cols)

        self.ship_alive = True
        self.ship_x = screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = screen_size[1] // 2 + 200
        self.ship_pos = [self.ship_x, self.ship_y]
        self.prev_select = False
        self.left_joystick = [0.0, 0.0]
        self.right_joystick = [0.0, 0.0]
        self.deadzone = 0.2
        self.cursor_pos = [screen_size[0] // 2, screen_size[1] // 2]
        self.cursor_speed = 1000
        self.selected_skill = None
        self.nav_cooldown = 150  # ms
        self.last_nav_time = 0

        self.input_mode = "mouse"
        self.last_input_time = 0

        self.hitpoints = Interface("assets/ui/status.png", 0, 40, 40,
                                   hud_ratio, ['right', 'bottom'])
        self.shield = Interface("assets/ui/shield_bar.png", 0, 40, 17,
                                hud_ratio, ['right', 'bottom'], 33, [0, -150])
        self.xp = Interface("assets/ui/xp.png", -1, 40, 17,
                            hud_ratio, ['right', 'bottom'], 33, [0, -175])
        self.ammo = Interface("assets/ui/ammo.png", 0, 11, 40,
                              hud_ratio, ['right', 'bottom'], 35, [-160, 0])
        self.credits = game_font.render(f"{self.ship.credits}€$", True, (255, 200, 0))

        self.anim_frame_base = 0
        self.anim_frame_overlay = 0
        self.anim_index_left = 0
        self.anim_index_right = 0
        self.cooldown_base = 100
        self.cooldown_overlay = 50
        self.anim_base_index = 0
        self.anim_base_direction = 1

        self.last_update_base = pg.time.get_ticks()
        self.last_update_overlay = pg.time.get_ticks()
        self.last_update = pg.time.get_ticks()
        self.last_update_left = pg.time.get_ticks()
        self.last_update_right = pg.time.get_ticks()
        self.last_direction = None
        self.last_time = pg.time.get_ticks()
        self.direction_set = None

        self.frames = []

        for i in range(self.cols):
            img = self.ship_sprite[0].get_image(i, framew, frameh, scale=self.scale,
                                                columns=self.cols)
            self.frames.append(img)

        self.left_frames_movement = self.frames[0:2]
        self.frame_idle = self.frames[2]
        self.right_frames_movement = self.frames[3:5]
        self.frames_flying = self.frames[5:9]
        self.base = self.frame_idle

        framew = self.explosion_sheet.sheet.get_width() // self.explosion_frames
        frameh = self.explosion_sheet.sheet.get_height()
        self.frame_explode = [
            self.explosion_sheet.get_image(i, framew, frameh, scale=self.scale,
                                           columns=self.explosion_frames)
            for i in range(self.explosion_frames)]

        framew = self.megaexplosion_sheet.sheet.get_width() // 4
        frameh = self.megaexplosion_sheet.sheet.get_height()
        self.frame_big_explode = [
            self.megaexplosion_sheet.get_image(i, framew, frameh,
                                               scale=self.scale, columns=4) for i in range(4)]

        self.stars = [[random.randint(0, screen_size[0]),
                       random.randint(0, screen_size[1]),
                       random.randint(1, 3)] for _ in range(100)]
        self.last_celestial_spawn = 0
        self.celestial_spawn_interval = random.randint(8000, 14_000)
        self.last_alien_spawn = 0
        self.alien_spawn_interval = random.randint(4000, 10_000)
        self.alien_spawn_count = random.randint(1, 5)
        self.formation = ["clutch", "line", "block"]

        self.ALIENLASER = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ALIENLASER, 800)

        self.last_asteroid_spawn = 0
        self.asteroid_spawn_interval = 600
        self.asteroid_spawn_count = 6
        self.asteroid_hitpoints = 8
        self.asteroid_speed = 8
        self.asteroid_increment_speed = 10
        self.last_upgrade_spawn = 0
        self.upgrade_spawn_interval = 24_000
        self.last_boss_spawn = 0
        self.last_shot_time = 0
        self.last_upgrade = None
        self.active_upgrade = None
        self.upgrade_start_time = 0
        self.upgrade_duration = 16_000

        self.charge_active = False
        self.charge_start_time = 0
        self.charge_duration = 2000
        self.charge_rumble = 0.3

        self.score = 0
        self.score_multiplier = 1.0
        self.high_score = 0
        self.active_mults = []
        self.survival_bonus = 0
        self.game_over = False

        self.skill_tab = Tab(
            "assets/ui/skill_tab.png",
            start_pos=(screen_size[0], 200),
            content_renderer=render_skills_tab)

        self.stats_tab = Tab(
            "assets/ui/skill_tab.png",
            start_pos=(100, screen_size[1]),
            content_renderer=render_stats_tab)

        self.skills = SkillManager()

        self.play_sound = True
        self.pause = False
        self.debugging = False

        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.milliseconds = 0
        self.stopwatch = None

        self.screen_shake = 0
        self.count = 0
        self.last_blink = 0

        self.cursor_sprite = pg.image.load(
            "assets/ui/cursor.png").convert_alpha()
        self.cursor_visible = False
        self.last_cursor_pos = pg.mouse.get_pos()
        self.last_move_time = pg.time.get_ticks()
        self.cursor_hide_delay = 3000

        if tutorial_on:
            self.tutorial = Tutorial()

        self.game_over_fx = True
        self.skills_generated = False
        fade.start("in")

        self.load_config()
        apply_volume(self)

        pg.mixer.music.play(-1)

    def run(self, running, clock, screen,
            screen_size, hud_padding, hud_ratio, crt, font):
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == self.ALIENLASER:
                    if not self.pause:
                        shooters = random.sample(self.aliens.sprites(), k=min(3, len(self.aliens)))
                        shots_this_frame = 0
                        for alien in shooters:
                            new_projectiles = alien.shoot(self.ship, alien.shot_cooldown)
                            if new_projectiles:
                                shots_this_frame += len(new_projectiles)
                                self.enemy_projectiles.add(*new_projectiles)

                        if shots_this_frame > 0 and self.play_sound:
                            self.sounds[0].play()

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_w:
                        increase_volume(self)

                    if event.key == pg.K_s:
                        decrease_volume(self)

                    if event.key == pg.K_c:
                        self.take_screenshot(screen)

                    if event.key == pg.K_TAB:
                        if not self.skill_tab.active:
                            if self.stats_tab.active:
                                self.stats_tab.close()
                            else:
                                self.stats_tab.open((100, screen_size[1] - self.stats_tab.height - 100))

                    if event.key == pg.K_f:
                        if self.ship.charges > 0:
                            self.ship.super_charge(joysticks, self.score, self.explosions,
                                                   self.entities, self.frame_explode,
                                                   self.frame_big_explode)
                            self.sounds[1].play()
                            self.screen_shake = 50
                    if event.key == pg.K_g:
                        if self.ship.base_ammo > 0:
                            self.sounds[2].play()
                            if self.ship.gun == "shotgun":
                                self.ship.gun = "beam"
                            else:
                                self.ship.gun = "shotgun"

                    if event.key == pg.K_z:
                        if event.mod & pg.KMOD_SHIFT:
                            crt.prog['curvature'].value = max(0.0,crt.prog['curvature'].value - 0.5)
                        else:
                            crt.prog['curvature'].value += 0.5

                    if event.key == pg.K_KP_PLUS:
                        hud_padding += 5
                        hud_ratio = set_hud(screen_size, hud_padding)

                    if event.key == pg.K_KP_MINUS:
                        hud_padding -= 5
                        if hud_padding < 0:
                            hud_padding = 0
                        hud_ratio = set_hud(screen_size, hud_padding)

                    if event.key == pg.K_l:
                        movement.lock_y = not movement.lock_y

                    if event.key == pg.K_r and self.game_over:
                        reboot(self, screen_size)

                    if event.key == pg.K_F2:
                        debug(self)

                    if event.key == pg.K_ESCAPE:
                        if not self.skill_tab.active:
                            self.pause = not self.pause

                    if event.key == pg.K_q and (event.mod & pg.KMOD_CTRL):
                        if self.pause and not self.skill_tab.active:
                            running = False

                    if event.key == pg.K_m:
                        self.play_sound = not self.play_sound
                        if not self.play_sound:
                            pg.mixer.music.stop()
                        else:
                            pg.mixer.music.play(-1)
                        self.save_config()


                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.input_mode != "controller":
                        self.input_mode = "mouse"
                        self.right_joystick = [0.0, 0.0]
                    self.last_input_time = pg.time.get_ticks()

                    if self.skill_tab.active and self.current_phase_options:
                        mouse_pos = pg.mouse.get_pos()
                        self.cursor_pos = list(mouse_pos)
                        tab_x, tab_y = self.skill_tab.pos
                        clicked_skill = None
                        mouse_rect = pg.Rect(mouse_pos[0], mouse_pos[1], 1, 1)

                        for skill in self.current_phase_options:
                            skill_rect = pygame.Rect(skill.pos[0], skill.pos[1],
                                                     skill.rect.width,skill.rect.height)
                            if skill_rect.colliderect(mouse_rect):
                                clicked_skill = skill
                                break

                        if clicked_skill:
                            self.selected_skill = clicked_skill
                            self.skills.unlock_or_upgrade(self.selected_skill,self.ship)
                            self.skill_tab.close()
                            self.current_phase_options = []
                            self.phase_ending = False
                            self.pause = False

                        for skill in self.current_phase_options:
                            skill.hovered = (skill == self.selected_skill)

                elif event.type == JOYBUTTONDOWN:
                    if event.button == 0:
                        new_projectiles = self.ship.shoot(gun_type=self.ship.gun)
                        self.projectiles.add(*new_projectiles)
                        self.last_shot_time = pg.time.get_ticks()

                        self.sounds[0].play()

                        if self.ship.gun == "shotgun":
                            self.screen_shake = 20

                    if event.button == 1:
                        if not self.skill_tab.active:
                            if self.stats_tab.active:
                                self.stats_tab.close()
                            else:
                                self.stats_tab.open((100, screen_size[1] - self.stats_tab.height - 100))

                    if event.button == 2:
                        if self.ship.base_ammo > 0:
                            self.sounds[2].play()
                            if self.ship.gun == "shotgun":
                                self.ship.gun = "beam"
                            else:
                                self.ship.gun = "shotgun"

                    if event.button == 3 and self.game_over:
                        reboot(self, screen_size)

                    if controller.get_button(4) and controller.get_button(5):
                        if not self.charge_active and self.ship.charges > 0:
                            self.charge_active = True
                            self.charge_start_time = pg.time.get_ticks()

                    elif event.button == 4:
                        movement.lock_y = not movement.lock_y

                    if event.button == 5:
                        if self.selected_skill and self.current_phase_options:
                            self.skills.unlock_or_upgrade(self.selected_skill,
                                                          self.ship)
                            self.skill_tab.close()
                            self.current_phase_options = []
                            self.phase_ending = False
                            self.pause = False

                    if event.button == 6:
                        if self.pause and not self.skill_tab.active:
                            running = False

                    if event.button == 7:
                        if not self.skill_tab.active:
                            self.pause = not self.pause

                elif event.type == JOYBUTTONUP:
                    if event.button in (4, 5) and self.charge_active:
                        self.ship.super_charge(joysticks, self.score, self.explosions,
                                               self.entities, self.frame_explode, self.frame_big_explode)
                        self.screen_shake = 50
                        self.charge_active = False
                        self.sounds[1].play()
                        if joysticks:
                            controller.stop_rumble()

                elif event.type == JOYHATMOTION:
                    if event.value == (0, 1):
                        increase_volume(self)
                    elif event.value == (1, 0):
                        self.take_screenshot(screen)
                    elif event.value == (0, -1):
                        decrease_volume(self)

                elif event.type == JOYAXISMOTION:
                    val = event.value if abs(
                        event.value) > self.deadzone else 0.0

                    if event.axis in (0, 1):
                        self.left_joystick[event.axis] = val
                        self.ship.moved_down = False
                    elif event.axis in (-1, 0):
                        self.ship.moved_down = True

                    elif event.axis in (2, 3):
                        if event.axis == 2:
                            self.right_joystick[0] = apply_curve(self, val)

                        elif event.axis == 3:
                            self.right_joystick[1] = apply_curve(self, val)

                        if val != 0:
                            self.cursor_visible = True
                            self.last_move_time = pg.time.get_ticks()

            if not running:
                break

            if self.charge_active:
                if joysticks:
                    controller.rumble(self.charge_rumble, 1, 50)
                charge_elapsed = pg.time.get_ticks() - self.charge_start_time
                charge_ratio = min(1.0, charge_elapsed / self.charge_duration)

            screen.fill((0, 0, 0))
            delta = clock.tick(self.fps) / 1000

            if not self.pause or self.skill_tab.active:
                update_controller(self, screen_size, delta)
                if not self.skill_tab.active:
                    update_movement(self, delta, screen_size)
                    update_credits(self, font)

            mouse_pos = pg.mouse.get_pos()
            hide_cursor(self, mouse_pos)

            if pg.time.get_ticks() - self.last_move_time > self.cursor_hide_delay:
                self.cursor_visible = False

            if not self.pause and not self.game_over:
                update_game(self, delta, screen_size, hud_padding)
                update_time(self)

            self.skill_tab.update()
            self.stats_tab.update()

            if tutorial_on:
                self.tutorial.update(self, delta)

            render_frame(self, screen, font, hud_padding)

            if not self.game_over:
                update_hud(self, font, screen, hud_ratio)

            current_mouse_pos = pg.mouse.get_pos()
            mouse_moved = (current_mouse_pos != self.last_cursor_pos)
            if mouse_moved and not joysticks:
                self.input_mode = "mouse"
                self.cursor_pos = list(current_mouse_pos)
            self.last_cursor_pos = current_mouse_pos

            if self.cursor_visible:
                pos = self.cursor_pos if self.input_mode == "controller" else pg.mouse.get_pos()
                screen.blit(self.cursor_sprite, (int(pos[0]), int(pos[1])))

            if self.game_over:
                game_lost(self, font, screen, screen_size)

            if self.screen_shake > 0:
                self.screen_shake -= 1

            render = [0, 0]
            if self.screen_shake:
                render = self.ship.taken_damage()
                if joysticks:
                    controller.rumble(0.5, 1, 20)
            if not self.game_over:
                screen.blit(pg.transform.scale(screen, screen_size), render)

            alpha = fade.update()
            if alpha > 0:
                fade_surface = pg.Surface(screen_size)
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))
            crt.render(screen)
        pg.quit()

    def spawnpoint(self, ship, screen_size, ship_sprite, cols):
        framew = ship_sprite[0].sheet.get_width() // cols
        x = screen_size[0] // 2 - framew // 2
        y = screen_size[1] // 2 + 200
        ship.rect.topleft = (x, y)
        ship.hitbox.center = ship.rect.center
        self.ship_pos = [x, y]

    def save_config(self):
        config_data = {
            "volume" : self.volume,
            "play_sound" : self.play_sound,
            "credits" : self.ship.credits,
            "high_score" : self.high_score
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f, indent=4)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                config_data = {}

            self.volume = config_data.get("volume", 1)
            self.play_sound = config_data.get("play_sound", True)
            self.ship.credits = config_data.get("credits", 0)
            self.high_score = config_data.get("high_score", 0)

    def take_screenshot(self, screen):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, ".imgs")
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, f"{timestamp}.png")
        pg.image.save(screen, save_path)