import pygame

class Ship(pygame.sprite.Sprite):
    def __init__(self, sprite_sheet, x, y, frame, width, height, scale=4,
                 columns=1):
        super().__init__()
        self.image = sprite_sheet.get_image(frame, width, height, scale, columns)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6,
                                        self.rect.height * -0.6)
        self.velocity = 8
        self.direction = "idle"
        self.shooting = False
        self.moving = False

    def update_position(self, x, y):
        self.rect.topleft = (x, y)
        self.hitbox.topleft = self.rect.topleft