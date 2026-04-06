import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, color, speed=16):
        super().__init__()
        self.image = pygame.Surface([4, 20], pygame.SRCALPHA)
        self.image.fill((*color, 255))
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

        if self.rect.bottom < 0:
            self.kill()