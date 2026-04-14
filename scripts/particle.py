import pygame
from scripts.constants import COLOR_WHITE


class Particle:
    def __init__(self, location, velocity, timer=50, color=COLOR_WHITE,
                 size=6, shrink=True, fade=True):
        self.location = pygame.Vector2(location)
        self.velocity = pygame.Vector2(velocity)
        self.timer = timer
        self.initial_timer = timer
        self.color = color
        self.size = size
        self.initial_size = size
        self.shrink = shrink
        self.fade = fade

    def update(self):
        self.location += self.velocity
        self.timer -= 1

        self.velocity *= 0.95

        if self.shrink:
            life_ratio = self.timer / self.initial_timer
            self.size = max(1, int(self.initial_size * life_ratio))

        return self.timer > 0

    def draw(self, screen):
        if self.timer <= 0:
            return

        alpha = 255
        if self.fade:
            alpha = int(255 * (self.timer / self.initial_timer))

        particle_surface = pygame.Surface(
            (self.size, self.size), pygame.SRCALPHA
        )
        particle_surface.fill((*self.color, alpha))

        rect = particle_surface.get_rect(
            center=(int(self.location.x), int(self.location.y))
        )
        screen.blit(particle_surface, rect)