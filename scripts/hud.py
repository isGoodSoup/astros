import pygame
from scripts.sheet import SpriteSheet

class Interface(pygame.sprite.Sprite):
    def __init__(self, path, frame, width, height, hud_ratio, hud_pos,
                 columns=29, offset=(0, 0), scale=4):
        super().__init__()
        self.sprite_sheet = SpriteSheet(path)
        self.buttons_sheet = SpriteSheet("assets/ui/buttons.png")
        self.frames = [self.sprite_sheet.get_image(i, width, height, scale, columns)
            for i in range(columns)]
        self.buttons = {
            "A" : self.buttons_sheet.get_image(0, width, height, scale, 4),
            "B": self.buttons_sheet.get_image(1, width, height, scale, 4),
            "X": self.buttons_sheet.get_image(2, width, height, scale, 4),
            "Y": self.buttons_sheet.get_image(3, width, height, scale, 4),
        }
        self.image = self.frames[frame]
        self.hud_x = hud_ratio[hud_pos[0]] - self.image.get_width()
        self.hud_y = hud_ratio[hud_pos[1]] - self.image.get_height()
        self.offset_x, self.offset_y = offset
        self.toggle_controls = False

    def update(self, ship, hud_ratio, hud_pos, frame, screen):
        frame = int(min(frame, len(self.frames) - 1))
        self.hud_x = hud_ratio[hud_pos[0]] - self.image.get_width() + self.offset_x
        self.hud_y = hud_ratio[hud_pos[1]] - self.image.get_height() + self.offset_y
        screen.blit(self.frames[frame], (self.hud_x, self.hud_y))
        if self.toggle_controls:
            self.hud_x = (hud_ratio['left'] - self.image.get_width() + self.offset_x)
            self.hud_y = (hud_ratio['bottom'] - self.image.get_height() + self.offset_y)
            screen.blit(self.buttons.get("A", "A"), (self.hud_x, self.hud_y))