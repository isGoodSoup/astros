import pygame

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, path="assets/projectile.png", scale=2, speed=16):
        super().__init__()
        self.image = pygame.image.load(path).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

        if self.rect.bottom < 0:
            self.kill()