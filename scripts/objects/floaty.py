import random

import pygame


class FloatingNumber(pygame.sprite.Sprite):
    def __init__(self, x, y, text, font, color=(255,255,0), lifetime=800,
                 speed=-60, font_size=24):
        super().__init__()
        self.base_image = font.render(str(text), True, color)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.start_y = y
        self.speed = speed
        self.drift_x = random.uniform(-0.5, 0.5)
        self.scale = 1.5
        self.angle = random.uniform(-8, 8)

        self.elapsed = 0
        self.lifetime = lifetime

    def update(self, delta):
        self.elapsed += delta * 1000
        progress = self.elapsed / self.lifetime

        if progress >= 1:
            self.kill()
            return

        ease = 1 - (1 - progress) ** 3
        self.rect.y = self.start_y + self.speed * ease
        self.rect.x += self.drift_x

        self.scale = 1.5 - 0.5 * progress
        self.angle *= 0.95

        self.image = pygame.transform.rotozoom(
            self.base_image, self.angle, self.scale)

        self.rect = self.image.get_rect(center=self.rect.center)

        alpha = int(255 * (1 - progress**2))
        self.image.set_alpha(alpha)