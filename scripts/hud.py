import pygame
from scripts.sheet import SpriteSheet

class Interface(pygame.sprite.Sprite):
    def __init__(self, screen_size, frame, width, height, scale=4,columns=29):
        super().__init__()
        self.sprite_sheet = SpriteSheet("assets/ui/status.png")
        self.frames = [self.sprite_sheet.get_image(i, width, height, scale, columns) for i
            in range(columns)]
        self.image = self.sprite_sheet.get_image(frame, width, height, scale,columns)
        self.hud_x = screen_size[0] - self.image.get_width() - 100
        self.hud_y = screen_size[1] - self.image.get_height() - 100

    def update(self, ship, frame, screen):
        frame = min(frame, len(self.frames) - 1)
        screen.blit(self.frames[frame], (self.hud_x, self.hud_y))