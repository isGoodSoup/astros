import pygame
import math

from scripts.settings import COLOR_LIGHT_RED


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, color, direction=(0, -1), speed=16,
                 damage=1, range_limit=900,
                 homing=False, screen=None, target=None,
                 explosive=False, explosion_radius=0):
        super().__init__()
        self.screen = screen
        self.speed = speed
        self.damage = damage
        self.direction = pygame.Vector2(direction).normalize()
        self.range_limit = range_limit
        self.distance_traveled = 0

        self.homing = homing
        self.target = target
        self.explosive = explosive
        self.explosion_radius = explosion_radius
        self.nuke = False

        if self.homing:
            radius = 6
            proj_color = COLOR_LIGHT_RED
            self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, proj_color, (radius, radius), radius)
        else:
            self.image = pygame.Surface((4, 20), pygame.SRCALPHA)
            self.image.fill((*color, 255))

            angle = -math.degrees(math.atan2(self.direction.y, self.direction.x)) - 90
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=pos)

    def update(self, delta_time=1.0):
        if self.homing and self.target and self.target.alive():
            tx, ty = self.target.rect.center
            target_vec = pygame.Vector2(tx - self.rect.centerx,
                                        ty - self.rect.centery)

            if target_vec.length() > 0:
                target_vec = target_vec.normalize()
                current = pygame.Vector2(self.direction)
                new_dir = current.lerp(target_vec, 0.08)
                self.direction = new_dir.normalize()

        dx = self.direction.x * self.speed * delta_time
        dy = self.direction.y * self.speed * delta_time
        self.rect.x += dx
        self.rect.y += dy
        self.distance_traveled += math.hypot(dx, dy)

        if self.distance_traveled >= self.range_limit:
            self.kill()