import pygame


class Particle:
    def __init__(self, location, velocity, timer=50, color=(255, 255, 255), radius=3):
        self.location = pygame.Vector2(location)
        self.velocity = pygame.Vector2(velocity)
        self.timer = timer
        self.color = color
        self.radius = radius

    def update(self):
        self.location += self.velocity
        self.timer -= 1

    def draw(self, screen):
        if self.timer > 0:
            pygame.draw.circle(screen, self.color, (int(self.location.x),
                                                int(self.location.y)), self.radius)