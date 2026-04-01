import pygame
from scripts.sheet import SpriteSheet

class Interface(pygame.sprite.Sprite):
    def __init__(self, path, frame, width, height, hud_ratio, columns=29,
                 offset=(0, 0), scale=4):
        super().__init__()
        self.sprite_sheet = SpriteSheet(path)
        self.frames = [self.sprite_sheet.get_image(i, width, height, scale, columns)
            for i in range(columns)]
        self.image = self.frames[frame]
        self.hud_x = hud_ratio['right'] - self.image.get_width()
        self.hud_y = hud_ratio['bottom'] - self.image.get_height()
        self.offset_x, self.offset_y = offset

    def update(self, ship, hud_ratio, frame, screen):
        frame = min(frame, len(self.frames) - 1)
        self.hud_x = hud_ratio['right'] - self.image.get_width() + self.offset_x
        self.hud_y = hud_ratio['bottom'] - self.image.get_height() + self.offset_y
        screen.blit(self.frames[frame], (self.hud_x, self.hud_y))