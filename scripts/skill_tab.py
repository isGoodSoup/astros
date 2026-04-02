import pygame

class Tab(pygame.sprite.Sprite):
    def __init__(self, image_path, start_pos, content_renderer=None, speed=16, scale=4):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(
            self.image,
            (self.image.get_width() * scale, self.image.get_height() * scale)
        )
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.rect = self.image.get_rect(topleft=start_pos)
        self.start_pos = pygame.Vector2(start_pos)
        self.pos = pygame.Vector2(start_pos)
        self.target_pos = pygame.Vector2(start_pos)
        self.speed = speed
        self.active = False
        self.content_renderer = content_renderer
        self.padding = 75

    def set_target(self, target_pos):
        self.target_pos = pygame.Vector2(target_pos)

    def update(self):
        dest = self.target_pos if self.active else self.start_pos
        direction = dest - self.pos
        if direction.length() > 0:
            move = direction.normalize() * min(self.speed, direction.length()) # type: ignore
            self.pos += move
            self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def render(self, screen, font=None):
        screen.blit(self.image, self.rect)
        if self.content_renderer:
            self.content_renderer(screen, self.rect, font)