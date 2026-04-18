import pygame

import scripts.system.assets as assets
from scripts.engine import runtime
from scripts.engine.clock import Clock
from scripts.engine.subtitle import SubtitleManager
from scripts.system.config import load_config
from scripts.system.events import Events
from scripts.system.fonts import FontManager
from scripts.engine.hud import HUD
from scripts.engine.input import Input
from scripts.system.mixer import Mixer
from scripts.engine.render import RenderScreen
from scripts.system.constants import *
from scripts.engine.fade import fade
from scripts.engine.skill import SkillManager
from scripts.system.soundlib import apply_volume
from scripts.engine.spawns import SpawnManager
from scripts.objects.sprites import SpriteManager
from scripts.system.state import GameState
from scripts.engine.tutorial import Tutorial
from scripts.engine.update import Updater

# Copyright (c) 2026 Diego
# Licensed under the MIT License. See LICENSE file for details.

local = None


class Game:
    def __init__(self, context, screen, screen_size, crt, hud_ratio, traits,
                 ships, ship_index=0):
        global local
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, SAVE_DIR_NAME)
        os.makedirs(save_dir, exist_ok=True)
        self.config_path = os.path.join(save_dir, CONFIG_FILE)

        self.local = context.local
        self.delta = 0
        self.screen = screen
        self.screen_size = screen_size
        self.hud_ratio = hud_ratio
        self.crt = crt
        self.running = True
        self.fps = FPS
        self.scale = SCALE
        self.hud_padding = HUD_PADDING

        self.state = GameState()
        self.input = Input(screen_size)
        self.clock = Clock()
        self.updater = Updater()
        self.font = FontManager(None, FONT_DEFAULT_SIZE)
        self.render = RenderScreen()
        self.ships = ships
        self.ship_index = ship_index
        self.sprites = SpriteManager(self)
        self.ship = self.sprites.ship
        self.hud = HUD(self, screen_size, hud_ratio, self.font.get_font())
        self.mixer = Mixer(self)
        self.events = Events()
        self.spawns = SpawnManager()
        self.subtitles = SubtitleManager(self)
        self.skills = SkillManager(self)
        self.traits = traits
        self.apply_traits()

        self.screen_shake_time = 0
        self.screen_shake_strength = 0
        self.last_blink = 0

        self.cursor_sprite = assets.CURSOR

        if TOGGLE_TUTORIAL:
            self.tutorial = Tutorial()

        load_config(self)
        runtime.current_game = self
        self.local.set_language(self.state.current_lang)
        local = self.local
        apply_volume(self)
        fade.start('in')
        self.mixer.queue([
            'odyssey',
            'unknown',
            'starfield'],
            loop=True)

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
                    self.events.alien_shoot_event(self)

            screen.fill(BACKGROUND)
            self.delta = clock.tick(self.fps) / ONE_SECOND

            self.input.update(self, events)
            self.input.act(self, events)
            self.updater.update(self)
            self.render.draw(self)

        pygame.quit()

    def apply_traits(self):
        for trait in self.traits:
            trait.ability.apply_on(self, self.ship)
