import pygame
from typing import Optional, Union
from os import PathLike

FileArg = Optional[Union[str, PathLike]]

class FontManager:
    def __init__(self, name: FileArg, size: int):
        pygame.font.init()
        self.size = size

        self.fonts = [
            pygame.font.Font("assets/fonts/Bytesized.ttf", size * 2),
            pygame.font.Font("assets/fonts/PressStart2P.ttf", size),
            pygame.font.Font("assets/fonts/BoldPixels.ttf", size * 2),
        ]

        if name is not None:
            self.fonts.insert(0, pygame.font.Font(name, size))

        self.linesizes = [32, 32, 32]
        self.font_index = 0
        self.linesize = self.linesizes[self.font_index]
        self.current_font = self.fonts[self.font_index]

    def get_font(self) -> pygame.font.Font:
        return self.current_font

    def get_linesize(self):
        self.linesize = self.linesizes[self.font_index]
        return self.linesize

    def render(self, text: str, antialias: bool, color, background=None) -> pygame.Surface:
        return self.current_font.render(text, antialias, color, background)

    def update(self) -> None:
        self.font_index = (self.font_index + 1) % len(self.fonts)
        self.current_font = self.fonts[self.font_index]