import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, cooldown=50):
        super().__init__()
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.center = self.rect.center  # store original center
        self.last_update = pygame.time.get_ticks()
        self.cooldown = cooldown

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.cooldown:
            self.last_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]
                self.rect = self.image.get_rect(center=self.center)