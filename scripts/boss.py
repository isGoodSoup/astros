import pygame

class Boss(pygame.sprite.Sprite):
    def __init__(self, ship, x, y, color, frame=0, width=32, height=32, scale=8,
                 columns=1, offset_x=0, offset_y=0):
        super().__init__()
        # self.sprite_sheet = SpriteSheet(f"assets/{color}_alien.png")
        self.image = pygame.image.load(f"assets/{color}_alien.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(self.rect.width * -0.5, self.rect.height * -0.5)

        self.pos = pygame.Vector2(x, y)
        self.frames = []
        self.ship = ship
        self.velocity = max(1, ship.velocity + 1)
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = "idle"
        self.shooting = False
        self.moving = False

        self.level = ship.level + 5
        self.max_hitpoints = 50 * self.level
        self.hitpoints = self.max_hitpoints
        self.base_damage = ship.damage * self.level
        self.last_shot_time = 0
        self.shot_cooldown = 150
        self.last_move = pygame.time.get_ticks()
        self.move_delay = 100
        self.hit = False

        self.target = pygame.Vector2(
            self.ship.rect.midbottom[0] + self.offset_x,
            self.offset_y
        )

    def update(self):
        self.hitbox.center = self.rect.center
        target_x = self.ship.rect.centerx + self.offset_x

        direction = self.target - self.pos

        if direction.length() > self.velocity:
            direction = direction.normalize()
            self.pos += direction * self.velocity
        else:
            self.pos = self.target

        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        if self.rect.top > pygame.display.Info().current_h or self.hitpoints <= 0:
            self.kill()