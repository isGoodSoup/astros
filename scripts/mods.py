import pygame

from scripts.fonts import FontManager
from scripts.game import Game
from scripts.shared import fade
from scripts.sheet import SpriteSheet

class Mods:
    def __init__(self, screen, screen_size, hud_ratio):
        fade.start("in")
        self.running = True
        self.screen_size = screen_size
        self.font = FontManager(None, 36)
        self.scale = 4
        self.preview_scale = 2
        self.ship_frames = 9

        self.ships = [
            SpriteSheet("assets/ship.png"),
            SpriteSheet("assets/ship_v2.png"),
            SpriteSheet("assets/ship_v3.png")
        ]

        self.current_ship_index = 0
        self.ship_previews = []
        self.ship_previews_large = []

        for sheet in self.ships:
            framew = sheet.sheet.get_width() // self.ship_frames
            frameh = sheet.sheet.get_height()
            idle_frame_index = 2

            preview = sheet.get_image(
                idle_frame_index,
                framew,
                frameh,
                scale=self.scale,
                columns=self.ship_frames
            ).convert_alpha()

            large_preview = pygame.transform.scale(
                preview,
                (preview.get_width() * self.preview_scale,
                 preview.get_height() * self.preview_scale)
            )

            self.ship_previews.append(preview)
            self.ship_previews_large.append(large_preview)

        w, h = self.ship_previews[0].get_size()
        self.dim_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.dim_surface.fill((0, 0, 0, 120))

    def run(self, clock, screen, screen_size, hud_ratio, crt):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.input(event, clock, screen,  screen_size, hud_ratio,
                           self.ships, self.current_ship_index, crt)

            if not self.running:
                break

            screen.fill((0, 0, 0))
            clock.tick(60)

            self.draw(screen)

            alpha = fade.update()
            if alpha > 0:
                fade_surface = pygame.Surface(screen_size)
                fade_surface.fill((0, 0, 0))
                fade_surface.set_alpha(alpha)
                screen.blit(fade_surface, (0, 0))

            crt.render(screen)

    def input(self, event, clock, screen, screen_size, hud_ratio, ships,
              ship_index, crt):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.current_ship_index = (self.current_ship_index - 1) % len(self.ship_previews)

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.current_ship_index = (self.current_ship_index + 1) % len(self.ship_previews)

            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                game = Game(screen, screen_size, hud_ratio, ships, ship_index)
                game.run(clock, screen, screen_size, hud_ratio, crt)
                fade.start("out")
                self.running = False

    def draw(self, screen):
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2

        header = "SHIP MODS"
        header_surf = self.font.render(header, True, (255, 206, 0))
        header_rect = header_surf.get_rect(center=(center_x, 100))
        screen.blit(header_surf, header_rect)

        current_preview = self.ship_previews_large[self.current_ship_index]
        rect = current_preview.get_rect(center=(center_x, center_y))
        screen.blit(current_preview, rect)

        offset = 200
        left_index = (self.current_ship_index - 1) % len(self.ship_previews)
        right_index = (self.current_ship_index + 1) % len(self.ship_previews)

        left_preview = self.ship_previews[left_index]
        right_preview = self.ship_previews[right_index]

        left_rect = left_preview.get_rect(center=(center_x - offset, center_y))
        right_rect = right_preview.get_rect(
            center=(center_x + offset, center_y))

        screen.blit(left_preview, left_rect)
        screen.blit(self.dim_surface, left_rect)

        screen.blit(right_preview, right_rect)
        screen.blit(self.dim_surface, right_rect)