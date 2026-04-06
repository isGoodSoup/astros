import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, color, direction=(0, -1), speed=16,
                 damage=1, range_limit=900):
        super().__init__()
        self.image = pygame.Surface([4, 20], pygame.SRCALPHA)
        self.image.fill((*color, 255))
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.damage = damage
        self.direction = direction
        self.range_limit = range_limit
        self.distance_traveled = 0

        angle = -math.degrees(math.atan2(direction[1], direction[0])) - 90
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self, delta_time=1.0):
        dx = self.direction[0] * self.speed * delta_time
        dy = self.direction[1] * self.speed * delta_time
        self.rect.x += dx
        self.rect.y += dy
        self.distance_traveled += math.sqrt(dx*dx + dy*dy)

        if self.distance_traveled >= self.range_limit:
            self.kill()