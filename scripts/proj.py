import pygame
from .sheet import SpriteSheet

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet_path="assets/projectile.png",
                 cols=4, scale=2, speed=16, anim_cooldown=100):
        super().__init__()
        self.sprite_sheet = SpriteSheet(sprite_sheet_path)
        sheet_width = self.sprite_sheet.sheet.get_width()
        sheet_height = self.sprite_sheet.sheet.get_height()
        frame_width = sheet_width // cols
        frame_height = sheet_height

        self.frames = [self.sprite_sheet.get_image(i, frame_width, frame_height, scale=scale, columns=cols)
                       for i in range(cols)]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

        self.last_update = pygame.time.get_ticks()
        self.anim_cooldown = anim_cooldown

    def update(self):
        self.rect.y -= self.speed

        if self.rect.bottom < 0:
            self.kill()

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.anim_cooldown:
            self.last_update = current_time
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]