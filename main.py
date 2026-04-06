import pygame as pg
from pygame.constants import *
from pygame.display import toggle_fullscreen

from scripts.shared import fade

from scripts.celestial import *
from scripts.crt import CRT
from scripts.game import Game
from scripts.soundlib import load_sounds
from scripts.update import set_hud

class Menu:
    def __init__(self):
        pg.init()
        pg.font.init()
        self.width = int(pg.display.Info().current_w)
        self.height = int(pg.display.Info().current_h)
        self.screen_size = (self.width, self.height)
        self.hud_padding = 100
        self.hud_ratio = set_hud(self.screen_size, self.hud_padding)
        self.virtual_screen = pg.display.set_mode(self.screen_size)
        self.render_surface = pg.Surface((1920, 1080))
        self.screen = pg.display.set_mode(self.screen_size, DOUBLEBUF|OPENGL, vsync=1)
        self.crt = CRT(self.screen, style=1, virtual_resolution=(1920, 1080),cpu_only=False)
        self.crt.prog['curvature'].value = 0.7
        self.font = "assets/ui/PressStart2P.ttf"
        self.logo_img = pygame.image.load("assets/ui/logo.png")
        self.logo_img = pygame.transform.scale(self.logo_img,
            (self.logo_img.get_width() * 4, self.logo_img.get_height() * 4))
        self.cursor_sprite = pg.image.load("assets/ui/cursor.png")
        self.game_font = pg.font.Font(self.font, 96)
        self.text_font = pg.font.Font(self.font, 24)
        icon = pg.image.load("assets/ui/icon.png")
        pg.display.set_caption("Astros")
        pg.display.set_icon(icon)
        self.clock = pg.time.Clock()
        self.sounds = load_sounds()
        self.running = True
        self.transitioning = False
        self.count = 0
        self.last_blink = 0
        pg.mouse.set_visible(False)
        toggle_fullscreen()

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN and not self.transitioning:
                        self.sounds[2].play()
                        fade.start("out")
                        self.transitioning = True
                elif event.type == JOYBUTTONDOWN:
                    if event.button in range(0, 9):
                        self.sounds[2].play()
                        fade.start("out")
                        self.transitioning = True

            alpha = fade.update()
            self.screen.fill((0, 0, 0))

            now = pg.time.get_ticks()
            if now - self.last_blink > 500:
                self.count += 1
                self.last_blink = now

            colors = [(255, 255, 255), (0, 0, 0, 0)]
            start = self.text_font.render("Press any key to start", True,
                                          colors[self.count % 2])
            title_y = 200
            self.render_surface.fill((0, 0, 0))
            surface_width, surface_height = self.render_surface.get_size()
            title_x = surface_width // 2 - self.logo_img.get_width() // 2
            start_x = surface_width // 2 - start.get_width() // 2
            self.render_surface.blit(self.logo_img, (title_x, title_y))
            self.render_surface.blit(start, (start_x, title_y + 600))
            self.screen.blit(pg.transform.scale(self.render_surface, self.screen_size),(0, 0))
            if alpha > 0:
                fade_surface = pg.Surface((1920, 1080))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                self.render_surface.blit(fade_surface, (0, 0))

            self.crt.render(self.render_surface)
            dt = self.clock.tick(60) / 1000

            if self.transitioning and not fade.active:
                self.init_game()
                return

    def init_game(self):
        game = Game(self.screen, self.screen_size,
                    self.hud_ratio, self.text_font)
        game.run(self.running, self.clock, self.screen,
                 self.screen_size, self.hud_padding,
                 self.hud_ratio, self.crt, self.text_font)

if __name__ == '__main__':
    menu = Menu()
    menu.run()