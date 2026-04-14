import random

from scripts.constants import ALIEN_COLORS, ALIEN_BASE_HITPOINTS
from scripts.entity import Entity


class Alien(Entity):
    def __init__(self, color, x, y):
        super().__init__(f"assets/aliens/{color}.png", x, y, scale=False)

        self.enable_hover(
            amplitude=8 + random.random() * 12,
            speed=0.8 + random.random() * 1.5
        )

        self.hitpoints = ALIEN_COLORS[color] * ALIEN_BASE_HITPOINTS

    def update(self):
        self.hover_around()
        self.rect.x += self._hover_speed
        if self.hitpoints <= 0:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)