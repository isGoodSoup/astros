import pygame

from scripts.proj import Projectile

class Alien(pygame.sprite.Sprite):
    def __init__(self, ship, x, y, color, frame, width=16, height=13, scale=4,
                 columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.image = pygame.image.load(f"assets/aliens/{color}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.6,
                                        self.rect.height * -0.6)
        self.pos = pygame.Vector2(x, y)
        self.frames = []
        self.ship = ship
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = "idle"
        self.shooting = False
        self.moving = False

        self.level = ship.level + 2
        self.max_hitpoints = 2 * self.level
        self.hitpoints = self.max_hitpoints
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = 200
        self.hit = False

    def update(self):
        self.hitbox.center = self.rect.center
        if self.rect.top > pygame.display.Info().current_h or self.hitpoints <= 0:
            self.kill()

    def shoot(self, base, shot_cooldown):
        current_time = pygame.time.get_ticks()
        self.shooting = False
        new_projectiles = []

        if current_time - self.last_shot_time >= shot_cooldown:
            projectile = Projectile(
                pos=[self.rect.centerx, self.rect.bottom],
                color=[0, 255, 100], direction=(0, 1), speed=12)
            self.shooting = True
            new_projectiles.extend([projectile])
            self.last_shot_time = current_time
        return new_projectiles