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

local = None


class Game:
    def __init__(self, context, screen_size, hud_ratio, traits,
                 ships, ship_index=0):
        global local
        home_dir = os.path.expanduser("~")
        save_dir = os.path.join(home_dir, SAVE_DIR_NAME)
        os.makedirs(save_dir, exist_ok=True)
        self.config_path = os.path.join(save_dir, CONFIG_FILE)
        self.local = context.local
        self.screen_size = screen_size
        self.hud_ratio = hud_ratio
        self.delta = 0
        self.fps = FPS

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

        # --- transient state ---
        self.screen_shake = 0
        self.last_blink = 0
        self.cursor_sprite = assets.CURSOR

        self.tutorial = Tutorial() if TOGGLE_TUTORIAL else None

        load_config(self)

        runtime.current_game = self
        self.local.set_language(self.state.current_lang)
        local = self.local

        apply_volume(self)
        fade.start('in')

        self.mixer.queue(['odyssey', 'unknown', 'starfield'], loop=True)

        self.running = True
        self.paused = False

    def update(self, delta, events):
        self.delta = delta
        self.input.update(self, events)
        self.input.act(self, events)

        # core simulation
        self.updater.update(self)

    def draw(self, screen):
        self.render.draw(self)

    def apply_traits(self):
        for trait in self.traits:
            trait.ability.apply_on(self, self.ship)

    def stop(self):
        self.running = False

    def pause(self, value=True):
        self.state.pause = value
        self.paused = value