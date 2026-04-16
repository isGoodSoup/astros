import pygame
import math

from scripts.system.constants import COLOR_LIGHT_RED
from scripts.engine.utils import resource_path


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

class StoneProjectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, game, speed=10, damage=1, parent=None):
        super().__init__()
        self.game = game
        self.speed = speed
        self.damage = damage
        self.direction = pygame.Vector2(direction).normalize()
        self.parent = parent
        self.pos = pygame.Vector2(pos)
        self.start_pos = pygame.Vector2(pos)
        self.max_dist = 400
        self.returning = False
        self.angle = 0

        try:
            self.image = pygame.image.load(resource_path("assets/asteroids/asteroid_small.png")).convert_alpha()
            self.image = pygame.transform.scale(self.image, (24, 24))
        except:
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 150, 150), (10, 10), 10)

        self.original_image = self.image
        self.rect = self.image.get_rect(center=pos)

    def update(self, delta_time=1.0):
        self.angle += 10
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        if not self.returning:
            move = self.direction * self.speed * delta_time
            self.pos += move
            if self.pos.distance_to(self.start_pos) >= self.max_dist:
                self.returning = True
        else:
            target = self.start_pos
            if self.parent and self.parent.alive():
                target = pygame.Vector2(self.parent.rect.center)

            dir_to_target = (target - self.pos)
            if dir_to_target.length() > 5:
                self.pos += dir_to_target.normalize() * self.speed * delta_time
            else:
                self.kill()

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if (self.pos.x < -100 or self.pos.x > self.game.screen_size[0] + 100 or
            self.pos.y < -100 or self.pos.y > self.game.screen_size[1] + 100):
            self.kill()