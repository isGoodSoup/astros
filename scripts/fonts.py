import pygame

from scripts.utils import resource_path


class FontManager:
    def __init__(self, name, size: int):
        pygame.font.init()
        self.size = size

        self.fonts = [
            pygame.font.Font(resource_path("assets/fonts/Monocraft.ttf"), size),
            pygame.font.Font(resource_path("assets/fonts/PressStart2P.ttf"), size),
            pygame.font.Font(resource_path("assets/fonts/BoldPixels.ttf"), size * 2),
        ]

        if name is not None:
            self.fonts.insert(0, pygame.font.Font(name, size))

        self.font_index = 0
        self.current_font = self.fonts[self.font_index]

    def get_font(self) -> pygame.font.Font:
        return self.current_font

    def get_linesize(self) -> int:
        return self.current_font.get_linesize()

    def render(self, text: str, antialias: bool, color, background=None) -> pygame.Surface:
        return self.current_font.render(text, antialias, color, background)

    def update(self) -> None:
        self.font_index = (self.font_index + 1) % len(self.fonts)
        self.current_font = self.fonts[self.font_index]