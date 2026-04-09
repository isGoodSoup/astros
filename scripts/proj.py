import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, color, direction=(0, -1), speed=16,
                 damage=1, range_limit=900,
                 homing=False, target=None,
                 explosive=False, explosion_radius=0):
        super().__init__()
        self.image = pygame.Surface([4, 20], pygame.SRCALPHA)
        self.image.fill((*color, 255))
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.damage = damage
        self.direction = direction
        self.range_limit = range_limit
        self.distance_traveled = 0

        self.homing = homing
        self.target = target
        self.explosive = explosive
        self.explosion_radius = explosion_radius
        self.nuke = False

        angle = -math.degrees(math.atan2(direction[1], direction[0])) - 90
        self.image = pygame.transform.rotate(self.image, angle)

    def update(self, delta_time=1.0):
        if self.homing and self.target:
            tx, ty = self.target.rect.center
            dx = tx - self.rect.centerx
            dy = ty - self.rect.centery

            vec = pygame.Vector2(dx, dy)
            if vec.length() > 0:
                vec = vec.normalize()

                current = pygame.Vector2(self.direction)
                new_dir = current.lerp(vec, 0.08)
                self.direction = (new_dir.x, new_dir.y)

        dx = self.direction[0] * self.speed * delta_time
        dy = self.direction[1] * self.speed * delta_time
        self.rect.x += dx
        self.rect.y += dy
        self.distance_traveled += math.sqrt(dx*dx + dy*dy)

        if self.distance_traveled >= self.range_limit:
            self.kill()