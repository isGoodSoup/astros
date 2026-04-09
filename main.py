from pygame.constants import *
from pygame.display import toggle_fullscreen

from scripts.fonts import FontManager
from scripts.shared import fade

from scripts.celestial import *
from scripts.crt import CRT
from scripts.game import Game
from scripts.soundlib import load_sounds
from scripts.update import set_hud

class Menu:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.width = int(pygame.display.Info().current_w)
        self.height = int(pygame.display.Info().current_h)
        self.screen_size = (self.width, self.height)
        self.hud_ratio = set_hud(self.screen_size)
        self.virtual_screen = pygame.display.set_mode(self.screen_size)
        self.render_surface = pygame.Surface((1920, 1080))
        self.screen = pygame.display.set_mode(self.screen_size, DOUBLEBUF|OPENGL, vsync=1)
        self.crt = CRT(self.screen, style=1, virtual_resolution=(1920, 1080),cpu_only=False)
        self.crt.prog['curvature'].value = 0.7
        self.font = FontManager(None, 24)
        self.logo_img = pygame.image.load("assets/ui/logo.png")
        self.logo_img = pygame.transform.scale(self.logo_img,
            (self.logo_img.get_width() * 4, self.logo_img.get_height() * 4))
        self.cursor_sprite = pygame.image.load("assets/ui/cursor.png")
        icon = pygame.image.load("assets/ui/icon.png")
        pygame.display.set_caption("Astros")
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.sounds = load_sounds()
        self.running = True
        self.transitioning = False
        self.count = 0
        self.last_blink = 0
        pygame.mouse.set_visible(False)
        toggle_fullscreen()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if any(pygame.key.get_pressed()) and not self.transitioning:
                        self.sounds[4].play()
                        fade.start("out")
                        self.transitioning = True
                elif event.type == JOYBUTTONDOWN:
                    if event.button in range(0, 9):
                        self.sounds[4].play()
                        fade.start("out")
                        self.transitioning = True

            alpha = fade.update()
            self.screen.fill((0, 0, 0))

            now = pygame.time.get_ticks()
            if now - self.last_blink > 500:
                self.count += 1
                self.last_blink = now

            colors = [(255, 255, 255), (0, 0, 0, 0)]
            start = (self.font.render("Press any key to start", True,
                                          colors[self.count % 2]))
            title_y = 200
            self.render_surface.fill((0, 0, 0))
            surface_width, surface_height = self.render_surface.get_size()
            title_x = surface_width // 2 - self.logo_img.get_width() // 2
            start_x = surface_width // 2 - start.get_width() // 2
            self.render_surface.blit(self.logo_img, (title_x, title_y))
            self.render_surface.blit(start, (start_x, title_y + 600))
            self.screen.blit(pygame.transform.scale(self.render_surface, self.screen_size),(0, 0))
            if alpha > 0:
                fade_surface = pygame.Surface((1920, 1080))
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                self.render_surface.blit(fade_surface, (0, 0))

            self.crt.render(self.render_surface)
            dt = self.clock.tick(60) / 1000

            if self.transitioning and not fade.active:
                self.init_game()
                return

    def init_game(self):
        game = Game(self.screen, self.screen_size, self.hud_ratio)
        game.run(self.clock, self.screen, self.screen_size, self.hud_ratio, self.crt)

if __name__ == '__main__':
    menu = Menu()
    menu.run()