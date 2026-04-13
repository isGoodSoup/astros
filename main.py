from pygame.constants import *
from pygame.display import toggle_fullscreen

import scripts.assets as assets
from scripts.celestial import *
from scripts.crt import CRT
from scripts.fonts import FontManager
from scripts.lang import local
from scripts.mixer import Mixer
from scripts.mods import Mods
from scripts.settings import *
from scripts.shared import fade
from scripts.soundlib import load_sounds
from scripts.update import set_hud
from scripts.utils import render_fade


class Menu:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.width = int(pygame.display.Info().current_w)
        self.height = int(pygame.display.Info().current_h)
        self.screen_size = (self.width, self.height)
        self.hud_ratio = set_hud(self.screen_size)
        self.render_surface = pygame.Surface(HD_RESOLUTION)
        self.screen = pygame.display.set_mode(self.screen_size, DOUBLEBUF|OPENGL, vsync=1)
        assets.load_assets()
        self.crt = CRT(self.screen, 1, HD_RESOLUTION, cpu_only=False)
        self.crt.prog['curvature'].value = CRT_CURVATURE
        self.font = FontManager(None, FONT_DEFAULT_SIZE)
        self.logo_img = assets.LOGO
        self.logo_img = pygame.transform.scale(self.logo_img,
            (self.logo_img.get_width() * SCALE, self.logo_img.get_height() * SCALE))
        pygame.display.set_caption("Astros")
        pygame.display.set_icon(assets.ICON)
        self.clock = pygame.time.Clock()
        self.mixer = Mixer()
        self.running = True
        self.transitioning = False
        self.last_blink = 0
        pygame.mouse.set_visible(False)
        toggle_fullscreen()
        fade.start('in')

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if any(pygame.key.get_pressed()) and not self.transitioning:
                        self.mixer.play(4)
                        fade.start('out')
                        self.transitioning = True
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button in range(0, 9):
                        self.mixer.play(4)
                        fade.start('out')
                        self.transitioning = True

            if not self.running:
                break

            alpha = render_fade(self.screen, self.screen_size)
            self.screen.fill(COLOR_BLACK)

            now = pygame.time.get_ticks()
            if now - self.last_blink > ONE_SECOND//2:
                self.last_blink = now

            start = self.font.render(local.t('menu.start'), True,
                                     COLOR_WHITE)
            title_y = TITLE_Y
            self.render_surface.fill(COLOR_BLACK)
            surface_width, surface_height = self.render_surface.get_size()
            title_x = surface_width // 2 - self.logo_img.get_width() // 2
            start_x = surface_width // 2 - start.get_width() // 2
            self.render_surface.blit(self.logo_img, (title_x, title_y))
            if (now // ONE_SECOND//2) % 2 == 0:
                self.render_surface.blit(start, (start_x, title_y + TITLE_OFFSET))
            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen_size),(0, 0))

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
        mods = Mods(self.screen, self.screen_size, self.hud_ratio)
        mods.run(self.clock, self.screen, self.screen_size, self.hud_ratio,
              self.crt)
        self.running = False

if __name__ == '__main__':
    menu = Menu()
    menu.run()