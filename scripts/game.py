import pygame

import scripts.assets as assets
from scripts import runtime
from scripts.clock import Clock
from scripts.config import load_config
from scripts.constants import *
from scripts.events import Events
from scripts.fonts import FontManager
from scripts.hud import HUD
from scripts.input import Input
from scripts.mixer import Mixer
from scripts.render import RenderScreen
from scripts.shared import fade
from scripts.skill import SkillManager
from scripts.soundlib import apply_volume
from scripts.spawns import SpawnManager
from scripts.sprites import SpriteManager
from scripts.state import GameState
from scripts.tutorial import Tutorial
from scripts.update import Updater

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

        load_config(self)
        runtime.current_game = self
        self.local.set_language(self.state.current_lang)
        local = self.local
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
                    # self.events.alien_shoot_event(self) # TODO restore
                    pass

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
