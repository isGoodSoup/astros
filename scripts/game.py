import json
import os
import random

import pygame

import scripts.assets as assets
from scripts.clock import Clock
from scripts.controller import update_controller
from scripts.events import Events
from scripts.fonts import FontManager
from scripts.game_over import game_lost
from scripts.hud import HUD
from scripts.input import Input, update_cursor
from scripts.mixer import Mixer
from scripts.movement import update_movement, update_ship_angle
from scripts.render import render_frame
from scripts.settings import *
from scripts.shared import joysticks, controller, fade
from scripts.ship import Ship
from scripts.skill import SkillManager
from scripts.soundlib import apply_volume
from scripts.state import GameState
from scripts.tutorial import Tutorial
from scripts.update import update_game


# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.
# All assets in this game are © 2026 Diego. See ASSETS_LICENSE.txt.

class Game:
    def __init__(self, screen, screen_size, crt, hud_ratio, ships,
                 ship_index=0):
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, SAVE_DIR_NAME)
        os.makedirs(save_dir, exist_ok=True)
        self.config_path = os.path.join(save_dir, CONFIG_FILE)

        self.crt = crt
        self.state = GameState()
        self.input = Input(screen_size)
        self.clock = Clock()
        self.font = FontManager(None, FONT_DEFAULT_SIZE)
        self.ship_sprite = ships
        self.selected_sheet = self.ship_sprite[ship_index]
        self.ship_frames = SHIP_FRAMES
        framew = self.selected_sheet.sheet.get_width() // self.ship_frames
        frameh = self.selected_sheet.sheet.get_height()
        self.frame = 0
        self.ship = Ship(self.selected_sheet, 0, 0, self.frame, framew, frameh,
                         columns=self.ship_frames)
        self.spawnpoint(self.ship, screen_size, self.selected_sheet,
                        self.ship_frames)
        self.hud = HUD(self, screen_size, hud_ratio, self.font.get_font())
        self.mixer = Mixer()
        self.events = Events()

        self.screen = screen
        self.screen_size = screen_size
        self.running = True
        self.fps = FPS
        self.scale = SCALE
        self.volume = DEFAULT_VOLUME
        self.hud_padding = HUD_PADDING

        self.celestials = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.upgrades = pygame.sprite.Group()
        self.floating_numbers = pygame.sprite.Group()
        self.fleets = []
        self.particles = []

        self.ship_frames = SHIP_FRAMES
        self.explosion_frames = 7
        self.explosion_sheet = assets.EXPLOSION_SHEET
        self.megaexplosion_sheet = assets.MEGAEXPLOSION_SHEET
        self.ship_alive = True

        self.anim_frame_base = 0
        self.anim_frame_overlay = 0
        self.anim_index_left = 0
        self.anim_index_right = 0
        self.cooldown_base = ANIM_COOLDOWN_BASE
        self.cooldown_overlay = ANIM_COOLDOWN_OVERLAY
        self.anim_base_index = 0
        self.anim_base_direction = 1

        self.last_update_base = self.last_update_overlay = (
            self).last_update = self.last_update_left = (
            self).last_update_right = self.last_time = pygame.time.get_ticks()
        self.last_direction = self.direction_set = None

        self.frames = []

        for i in range(self.ship_frames):
            img = self.selected_sheet.get_image(i, framew, frameh,scale=self.scale,
                                                columns=self.ship_frames)
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
                columns=self.explosion_frames) for i in range(
                self.explosion_frames)]

        framew = self.megaexplosion_sheet.sheet.get_width() // 4
        frameh = self.megaexplosion_sheet.sheet.get_height()
        self.frame_big_explode = [
            self.megaexplosion_sheet.get_image(i, framew, frameh, scale=self.scale * 2,
                                               columns=4) for i in range(4)]

        self.stars = [[random.randint(0, screen_size[0]),
                       random.randint(0, screen_size[1]),
                       random.randint(1, 3)] for _ in range(STAR_COUNT)]

        self.boss_invisible_start = pygame.time.get_ticks()
        self.boss_invisible_duration = BOSS_INVISIBLE_DURATION

        self.last_celestial_spawn = 0
        self.celestial_spawn_interval = random.randint(
            *CELESTIAL_SPAWN_INTERVAL)
        self.last_reinforcement_spawn = 0
        self.last_alien_spawn = 0
        self.alien_spawn_interval = random.randint(*ALIEN_SPAWN_INTERVAL_RANGE)

        self.ALIENLASER = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ALIENLASER, ALIEN_SHOT_TIMER_MS)

        self.delay = pygame.time.get_ticks() + ALIEN_INITIAL_DELAY
        self.last_asteroid_spawn = 0
        self.asteroid_spawn_interval = ASTEROID_SPAWN_INTERVAL
        self.asteroid_hitpoints = ASTEROID_HITPOINTS
        self.asteroid_speed = ASTEROID_SPEED
        self.last_upgrade_spawn = 0
        self.upgrade_spawn_interval = UPGRADE_SPAWN_INTERVAL
        self.last_boss_spawn = 0
        self.last_shot_time = 0
        self.last_upgrade = None
        self.active_upgrade = None
        self.upgrade_start_time = 0

        self.skills = SkillManager()

        self.shockwaves = []
        self.nuke_flash = 0

        self.screen_shake = 0
        self.last_blink = 0

        self.cursor_sprite = assets.CURSOR

        if TOGGLE_TUTORIAL:
            self.tutorial = Tutorial()

        self.load_config()
        apply_volume(self)
        fade.start('in')
        self.mixer.queue(['odyssey', 'starfield'], loop=True)

    def run(self, clock, screen, screen_size, hud_ratio, crt):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.mixer.MUSIC_END:
                    self.mixer.next_track()

                if event.type == self.ALIENLASER and not self.state.pause and not self.state.game_over:
                    if pygame.time.get_ticks() < self.delay:
                        continue
                    shots_this_frame = 0
                    if random.random() > 0.5:
                        shooters = random.sample(self.aliens.sprites(),
                                                 k=min(1, len(self.aliens)))
                    else:
                        shooters = [alien for alien in self.aliens.sprites()
                                    if abs(alien.rect.centerx -
                                           self.ship.rect.centerx) <= CROSSHAIRS]

                    for alien in shooters:
                        new_projectiles = alien.shoot(self.ship,
                                                      alien.shot_cooldown)
                        if new_projectiles:
                            shots_this_frame += len(new_projectiles)
                            self.enemy_projectiles.add(*new_projectiles)

                    if shots_this_frame > 0 and self.state.play_sound:
                        self.mixer.sounds[0].play()

            screen.fill(BACKGROUND)
            delta = clock.tick(self.fps) / 1000

            self.input.update(self, events)
            self.input.act(self, events)

            if not self.state.pause or self.hud.skill_tab.active:
                update_controller(self, screen_size, delta)
                if not self.hud.skill_tab.active:
                    update_movement(self, delta, screen_size)
                    update_cursor(self, delta, screen_size)
                    update_ship_angle(self)

            if not self.state.pause and not self.state.game_over:
                update_game(self, delta, screen_size, self.hud_padding)
                self.clock.update_time(self)

            if TOGGLE_TUTORIAL:
                self.tutorial.update(self, delta)

            render_frame(self, screen, self.font, self.hud_padding)

            if not self.state.game_over:
                self.hud.update(self, self.font, screen, hud_ratio,
                                self.hud_padding)

            if self.input.cursor_visible:
                pos = self.input.cursor_pos if self.input.mode == "controller" else pygame.mouse.get_pos()
                screen.blit(self.cursor_sprite, (int(pos[0]), int(pos[1])))

            if self.state.game_over:
                game_lost(self, self.font, screen, screen_size)

            if self.screen_shake > 0:
                self.screen_shake -= 1
            render_offset = self.ship.taken_damage() if self.screen_shake else [0, 0]
            if joysticks and self.screen_shake:
                controller.rumble(0.5, 1, BASE_RUMBLE_MS)

            if not self.state.game_over:
                screen.blit(pygame.transform.scale(screen, screen_size),
                            render_offset)

            alpha = fade.update()
            if alpha > 0:
                fade_surface = pygame.Surface(screen_size)
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

            crt.render(screen)
        pygame.quit()

    def spawnpoint(self, ship, screen_size, ship_sprite, cols):
        framew = ship_sprite.sheet.get_width() // cols
        x = screen_size[0] // 2 - framew // 2
        y = screen_size[1] // 2 + SHIP_OFFSETS[1]
        ship.rect.topleft = (x, y)
        ship.hitbox.center = ship.rect.center

    def save_config(self):
        config_data = {
            "volume": self.volume,
            "play_sound": self.state.play_sound,
            "credits": self.ship.credits,
            "high_score": self.state.high_score
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
            self.state.play_sound = config_data.get("play_sound", True)
            self.ship.credits = config_data.get("credits", 0)
            self.state.high_score = config_data.get("high_score", 0)