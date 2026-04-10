import math

import pygame

import scripts.assets as assets
from scripts.fonts import FontManager
from scripts.game import Game
from scripts.shared import fade, joysticks


class Mods:
    def __init__(self, screen, screen_size, hud_ratio):
        fade.start("in")
        self.running = True
        self.screen_size = screen_size
        self.font = FontManager(None, 36)
        self.scale = 4
        self.preview_scale = 2
        self.ship_frames = 9
        self.ship_flying = False
        self.flight_speed = 16
        self.flight_offset = 0
        self.fade_started = False

        self.ships = assets.SHIPS

        self.selected_ship_index = None
        self.current_ship_index = 0
        self.ship_previews = []
        self.ship_previews_large = []

        for sheet in self.ships:
            framew = sheet.sheet.get_width() // self.ship_frames
            frameh = sheet.sheet.get_height()
            idle_frame_index = 2

            preview = sheet.get_image(idle_frame_index,
                framew, frameh, scale=self.scale, columns=self.ship_frames).convert_alpha()

            large_preview = pygame.transform.scale(preview,
                (preview.get_width() * self.preview_scale,
                 preview.get_height() * self.preview_scale))

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
                self.input(event, clock, screen, screen_size, hud_ratio, crt)

            if self.ship_flying:
                self.flight_offset -= self.flight_speed

                if not self.fade_started:
                    fade.start("out")
                    self.fade_started = True

            screen.fill((0, 0, 0))
            clock.tick(60)
            self.draw(screen)

            crt.render(screen)

            alpha = fade.update()
            if self.ship_flying and self.fade_started and alpha >= 255:
                self.running = False
                game = Game(screen, screen_size,
                            hud_ratio, self.ships, self.selected_ship_index)
                game.run(clock, screen, screen_size, hud_ratio, crt)

    def input(self, event, clock, screen, screen_size, hud_ratio, crt):
        if self.ship_flying:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.current_ship_index = ((self.current_ship_index - 1)
                                           % len(self.ship_previews))

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.current_ship_index = ((self.current_ship_index + 1)
                                           % len(self.ship_previews))

            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.ship_flying = True
                self.selected_ship_index = self.current_ship_index

        if joysticks:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.ship_flying = True
                    self.selected_ship_index = self.current_ship_index

                if event.button == 5:
                    self.current_ship_index = ((self.current_ship_index + 1)
                                               % len(self.ship_previews))

                if event.button == 4:
                    self.current_ship_index = ((self.current_ship_index - 1)
                                               % len(self.ship_previews))

    def draw(self, screen):
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2
        time = pygame.time.get_ticks()

        ship_float = 4 * math.sin(time * 0.0025)
        if self.ship_flying:
            ship_float += self.flight_offset

        current_preview = self.ship_previews_large[self.current_ship_index]
        rect = current_preview.get_rect(
            center=(center_x, center_y + int(ship_float)))
        screen.blit(current_preview, rect)

        offset = 200
        phase = math.pi / 2

        left_index = (self.current_ship_index - 1) % len(self.ship_previews)
        right_index = (self.current_ship_index + 1) % len(self.ship_previews)

        left_float = 2 * math.sin(time * 0.0025 + phase)
        right_float = 2 * math.sin(time * 0.0025 - phase)

        left_preview = self.ship_previews[left_index]
        right_preview = self.ship_previews[right_index]

        left_rect = left_preview.get_rect(center=(center_x - offset, center_y + int(left_float)))
        right_rect = right_preview.get_rect(center=(center_x + offset, center_y + int(right_float)))

        screen.blit(left_preview, left_rect)
        screen.blit(self.dim_surface, left_rect)

        screen.blit(right_preview, right_rect)
        screen.blit(self.dim_surface, right_rect)

        header_float = 4 * math.sin(time * 0.002)

        header = "STYLES"
        header_surf = self.font.render(header, True, (255, 206, 0))
        header_rect = header_surf.get_rect(
            center=(center_x, 100 + int(header_float)))
        screen.blit(header_surf, header_rect)