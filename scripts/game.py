import json
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
from scripts.skill import SkillManager
from scripts.soundlib import apply_volume
from scripts.spawns import SpawnManager
from scripts.sprites import SpriteManager
from scripts.state import GameState
from scripts.tutorial import Tutorial
from scripts.update import update_game
from scripts.utils import render_fade


# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.

class Game:
    def __init__(self, screen, screen_size, crt, hud_ratio, traits, ships,
                 ship_index=0):
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, SAVE_DIR_NAME)
        os.makedirs(save_dir, exist_ok=True)
        self.config_path = os.path.join(save_dir, CONFIG_FILE)

        self.delta = 0
        self.screen = screen
        self.screen_size = screen_size
        self.crt = crt
        self.running = True
        self.fps = FPS
        self.scale = SCALE
        self.hud_padding = HUD_PADDING

        self.state = GameState()
        self.input = Input(screen_size)
        self.clock = Clock()
        self.font = FontManager(None, FONT_DEFAULT_SIZE)
        self.ships = ships
        self.ship_index = ship_index
        self.sprites = SpriteManager(self)
        self.ship = self.sprites.ship
        self.hud = HUD(self, screen_size, hud_ratio, self.font.get_font())
        self.mixer = Mixer()
        self.events = Events()
        self.spawns = SpawnManager()
        self.skills = SkillManager()
        self.traits = traits
        self.apply_traits()

        self.screen_shake = 0
        self.last_blink = 0

        self.cursor_sprite = assets.CURSOR

        if TOGGLE_TUTORIAL:
            self.tutorial = Tutorial()

        self.load_config()
        apply_volume(self)
        fade.start('in')
        self.mixer.queue(['odyssey', 'unknown', 'starfield'], loop=True)

    def run(self, clock, screen, screen_size, hud_ratio, crt):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.events.MUSIC_END:
                    self.mixer.next_track()

                if (event.type == self.events.ALIENLASER and not
                self.state.pause and not self.state.game_over):
                    if pygame.time.get_ticks() < self.sprites.alien_delay:
                        continue
                    shots_this_frame = 0
                    if random.random() > 0.5:
                        shooters = random.sample(self.sprites.aliens.sprites(),
                                                 k=min(1, len(self.sprites.aliens)))
                    else:
                        shooters = [alien for alien in self.sprites.aliens.sprites()
                                    if abs(alien.rect.centerx -
                                           self.ship.rect.centerx) <= CROSSHAIRS]

                    for alien in shooters:
                        new_projectiles = alien.shoot(self.ship,
                                                      alien.shot_cooldown)
                        if new_projectiles:
                            shots_this_frame += len(new_projectiles)
                            self.sprites.enemy_projectiles.add(*new_projectiles)

                    if shots_this_frame > 0 and self.state.play_sound:
                        self.mixer.play(0)

            screen.fill(BACKGROUND)
            self.delta = clock.tick(self.fps) / ONE_SECOND

            self.input.update(self, events)
            self.input.act(self, events)

            if not self.state.pause or self.hud.skill_tab.active:
                update_controller(self, screen_size, self.delta)
                if not self.hud.skill_tab.active:
                    update_movement(self, self.delta, screen_size)
                    update_cursor(self, self.delta, screen_size)
                    update_ship_angle(self)

            if not self.state.pause and not self.state.game_over:
                update_game(self, self.delta, screen_size, self.hud_padding)
                self.clock.update_time(self)

            if TOGGLE_TUTORIAL:
                self.tutorial.update(self, self.delta)

            render_frame(self, screen, self.font, self.hud_padding)

            if not self.state.game_over and self.state.can_show_hud:
                self.hud.update(self, self.font, screen, hud_ratio,
                                self.hud_padding)

            if self.input.cursor_visible:
                pos = self.input.cursor_pos if self.input.mode == INPUT_CONTROLLER else pygame.mouse.get_pos()
                screen.blit(self.cursor_sprite, (int(pos[0]), int(pos[1])))

            if self.state.game_over:
                game_lost(self, self.font, screen, screen_size)

            if self.state.can_screen_shake:
                if self.screen_shake > 0:
                    self.screen_shake -= 1

                render_offset = self.ship.taken_damage() if self.screen_shake else [0, 0]
                if joysticks and self.screen_shake and self.state.can_rumble:
                    controller.rumble(1, 2, BASE_RUMBLE_MS + 20)

                if not self.state.game_over:
                    screen.blit(pygame.transform.scale(screen, screen_size),
                                render_offset)

            alpha = render_fade(screen, screen_size)
            crt.render(screen)
        pygame.quit()

    def apply_traits(self):
        for trait in self.traits:
            trait.ability.apply_on(self, self.ship)

    def save_config(self):
        config_data = {
            "music_volume": self.mixer.music_volume,
            "sfx_volume": self.mixer.sfx_volume,
            "play_sound": self.state.play_sound,
            "screen_shake": self.state.can_screen_shake,
            "rumble": self.state.can_rumble,
            "show_controls": self.state.can_show_controls,
            "show_hud": self.state.can_show_hud,
            "high_score": self.state.high_score,
            "language": self.state.current_lang,
        }
        with open(self.config_path, "w") as f:
            json.dump(config_data, f, indent=INDENTS)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                config_data = {}

            self.mixer.music_volume = config_data.get("music_volume", MUSIC_VOLUME)
            self.mixer.sfx_volume = config_data.get("sfx_volume", SFX_VOLUME)
            self.state.play_sound = config_data.get("play_sound", True)
            self.state.can_screen_shake = config_data.get("screen_shake", True)
            self.state.can_rumble = config_data.get("rumble", True)
            self.state.can_show_controls = config_data.get("show_controls", True)
            self.state.can_show_hud = config_data.get("show_hud", True)
            self.state.high_score = config_data.get("high_score", 0)
            self.state.current_lang = config_data.get("language", "en")