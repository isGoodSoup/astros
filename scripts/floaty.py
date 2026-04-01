import pygame

class FloatingNumber(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color=(255, 255, 0), lifetime=800, speed=-1):
        super().__init__()
        self.font = pygame.font.Font("assets/ui/PressStart2P.ttf", 24)
        self.image = self.font.render(str(text), True, color)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed > self.lifetime:
            self.kill()
        else:
            alpha = max(0, 255 - int(255 * (elapsed / self.lifetime)))
            self.image.set_alpha(alpha)