import pygame

class Boss(pygame.sprite.Sprite):
    def __init__(self, ship, x, y, color, frame=0, width=32, height=32, scale=8,
                 columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.image = pygame.image.load(f"assets/aliens/{color}.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width * scale, height * scale))
        self.rect = self.image.get_rect(center=(x,y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.5, self.rect.height * -0.5)

        self.pos = pygame.Vector2(x, y)
        self.ship = ship
        self.step = max(1, ship.velocity + 1)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = 1
        self.shooting = False
        self.moving = False

        self.colors = {'red' : 100, 'green' : 200, 'yellow' : 300}
        self.level = ship.level + 5
        self.max_hitpoints = 50 * self.level + self.colors.get(color)
        self.hitpoints = self.max_hitpoints
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = 150
        self.last_move = pygame.time.get_ticks()
        self.move_delay = 800
        self.move_timer = pygame.time.get_ticks()
        self.hit = False

        self.target = pygame.Vector2(
            self.ship.rect.midbottom[0] + self.offset_x,
            self.offset_y
        )

    def update(self):
        self.hitbox.center = self.rect.center

        now = pygame.time.get_ticks()
        if now - self.move_timer >= self.move_delay:

            screen_width = pygame.display.Info().current_w
            if self.rect.right >= screen_width or self.rect.left <= 0:
                self.direction *= -1
                self.rect.y += 30

            self.rect.x += self.direction * self.step
            self.rect.x = max(0, min(self.rect.x, screen_width - self.rect.width))
            self.move_timer = now