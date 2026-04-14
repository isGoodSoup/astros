import pygame

from scripts.shared import fade
from scripts.fonts import FontManager
from scripts.constants import (LINE_TIMER, FONT_DEFAULT_SIZE,
                              COLOR_WHITE, COLOR_BLACK, FPS)
from scripts.utils import render_fade


class Intro:
    def __init__(self, context, screen, clock, crt):
        fade.start('in')
        self.screen = screen
        self.clock = clock
        self.context = context
        self.crt = crt
        self.screen_size = (pygame.display.Info().current_w,
                            pygame.display.Info().current_h)
        self.lang = context.local
        self.lines = [
            self.lang.t('game.intro.line1'),
            self.lang.t('game.intro.line2'),
            self.lang.t('game.intro.line3'),
            self.lang.t('game.intro.line4')
        ]

        self.timer_per_line = LINE_TIMER  # e.g., 2500 milliseconds
        self.font = FontManager(None, FONT_DEFAULT_SIZE).get_font()
        self.running = True

        self.current_line_index = 0
        self.last_switch_time = pygame.time.get_ticks()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            current_time = pygame.time.get_ticks()
            if current_time - self.last_switch_time >= self.timer_per_line:
                self.current_line_index += 1
                self.last_switch_time = current_time

                if self.current_line_index >= len(self.lines):
                    fade.start('out')
                    self.running = False
                    return

                fade.start('in')

            self.screen.fill(COLOR_BLACK)
            self.clock.tick(FPS)
            self.display()
            alpha = render_fade(self.screen, self.screen_size)
            self.crt.render(self.screen)

    def display(self):
        if self.current_line_index < len(self.lines):
            line = self.lines[self.current_line_index]
            surf = self.font.render(line, True, COLOR_WHITE)
            alpha = fade.update()
            self.screen.blit(surf,
                (self.screen_size[0] // 2 - surf.get_width() // 2,
                    self.screen_size[1] // 2 - surf.get_height() // 2))
