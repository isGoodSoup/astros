import json

from pygame.constants import *

import scripts.system.assets as assets
from scripts.engine.difficulty import Difficulty
from scripts.objects.celestial import *
from scripts.system.context import AppContext
from scripts.engine.crt import CRT
from scripts.system.fonts import FontManager
from scripts.engine.game import Game
from scripts.system.mixer import Mixer
from scripts.engine.mods import Mods
from scripts.system.constants import *
from scripts.engine.fade import fade
from scripts.engine.update import set_hud
from scripts.engine.utils import render_fade
from scripts.engine.shared import controller


class Menu:
    def __init__(self, context):
        self.context = context
        pygame.init()
        pygame.font.init()
        self.width = int(pygame.display.Info().current_w)
        self.height = int(pygame.display.Info().current_h)
        self.screen_size = (self.width, self.height)
        self.hud_ratio = set_hud(self.screen_size)
        self.render_surface = pygame.Surface(HD_RESOLUTION)
        self.screen = pygame.display.set_mode(self.screen_size,
                                              DOUBLEBUF | OPENGL, vsync=1)
        assets.load_assets()
        self.crt = CRT(self.screen, 1, HD_RESOLUTION, cpu_only=False)
        self.crt.prog['curvature'].value = CRT_CURVATURE
        self.font = FontManager(None, FONT_DEFAULT_SIZE)
        self.logo_img = assets.LOGO
        self.logo_img = pygame.transform.scale(self.logo_img,
                                               (self.logo_img.get_width() * SCALE,
                                                self.logo_img.get_height() * SCALE))
        pygame.display.set_caption("Astros")
        pygame.display.set_icon(assets.ICON)
        self.clock = pygame.time.Clock()
        self.mixer = Mixer()
        self.running = True
        self.transitioning = False
        self.last_blink = 0
        self.skip = False
        pygame.mouse.set_visible(False)
        fade.start('in')

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.mod & KMOD_CTRL and event.key == K_s:
                        self.skip = True

                    if any(pygame.key.get_pressed()) and not self.transitioning:
                        self.mixer.play(4)
                        fade.start('out')
                        self.transitioning = True
                elif event.type == pygame.JOYBUTTONDOWN:
                    if controller.get_button(8) and controller.get_button(9):
                        self.skip = True

                    if event.button in range(0, 9):
                        self.mixer.play(4)
                        fade.start('out')
                        self.transitioning = True

            if not self.running:
                break

            alpha = render_fade(self.screen, self.screen_size)
            self.screen.fill(COLOR_BLACK)

            now = pygame.time.get_ticks()
            if now - self.last_blink > ONE_SECOND // 2:
                self.last_blink = now

            start_text = self.context.local.t('menu.start')
            start = self.font.render(start_text, True, COLOR_WHITE)

            title_y = TITLE_Y
            self.render_surface.fill(COLOR_BLACK)
            surface_width, surface_height = self.render_surface.get_size()
            title_x = surface_width // 2 - self.logo_img.get_width() // 2
            start_x = surface_width // 2 - start.get_width() // 2
            self.render_surface.blit(self.logo_img, (title_x, title_y))
            if (now // ONE_SECOND // 2) % 2 == 0:
                self.render_surface.blit(start, (start_x, title_y +
                                                 TITLE_OFFSET))
            version_text = self.context.local.t('menu.game_version')
            version = self.font.render(version_text, True, COLOR_WHITE)
            self.render_surface.blit(
                version,
                (VERSION_PADDING,
                surface_height - version.get_height() -
                VERSION_PADDING))

            self.screen.blit(
                pygame.transform.scale(
                    self.render_surface,
                    self.screen_size),
                (0, 0))

            if alpha > 0:
                fade_surface = pygame.Surface(HD_RESOLUTION)
                fade_surface.fill(COLOR_BLACK)
                fade_surface.set_alpha(alpha)
                self.render_surface.blit(fade_surface, (0, 0))

            self.crt.render(self.render_surface)
            dt = self.clock.tick(FPS) / ONE_SECOND

            if self.transitioning and not fade.active:
                self.init_game()
                return

    def init_game(self):
        if TOGGLE_SKIP or self.skip:
            game = (Game(self.context, self.screen, self.screen_size, self.crt,
                         self.hud_ratio, [], assets.SHIPS, 0))
            game.state.difficulty = Difficulty.EXPLORER
            game.run(self.clock, self.screen, self.screen_size,
                     self.hud_ratio, self.crt)
            self.running = False
        else:
            mods = Mods(self.context, self.screen, self.screen_size,
                        self.hud_ratio)
            mods.run(self.clock, self.screen, self.screen_size, self.hud_ratio,
                     self.crt)
        self.running = False


def load_language():
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, SAVE_DIR_NAME, CONFIG_FILE)

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            return config.get("language", "en")
        except (json.JSONDecodeError, ValueError):
            pass
    return "en"


if __name__ == "__main__":
    lang = load_language()
    context = AppContext(lang)
    menu = Menu(context)
    menu.run()
