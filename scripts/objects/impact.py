import pygame


class ImpactFrame(pygame.sprite.Sprite):
    def __init__(self, x, y, image, duration=50):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.spawn_time = pygame.time.get_ticks()
        self.duration = duration

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()