import pygame

from scripts.system.constants import SUBTITLE_DURATION, COLOR_WHITE


class Subtitle:
    def __init__(self, text, duration, color=COLOR_WHITE):
        self.text = text
        self.duration = duration
        self.color = color
        self.start_time = pygame.time.get_ticks()

class SubtitleManager:
    def __init__(self, game):
        self.game = game
        self.active = []

    def add(self, text, duration=SUBTITLE_DURATION, color=COLOR_WHITE):
        if not self.game.state.show_subtitles:
            return

        self.active.append(Subtitle(text, duration, color))
        if len(self.active) > 4:
            self.active.pop(0)

    def update(self):
        now = pygame.time.get_ticks()
        self.active = [
            s for s in self.active
            if now - s.start_time < s.duration
        ]

    def draw(self):
        y_offset = 0
        for s in self.active:
            surf = self.game.font.render(s.text, True, s.color)
            x = self.game.screen_size[0] // 2 - surf.get_width() // 2
            y = self.game.screen_size[1] - 100 - y_offset
            self.game.screen.blit(surf, (x, y))
            y_offset += 25