import math
import random

import pygame

from scripts.constants import ENTITY_HITBOX, SCALE
from scripts.utils import resource_path


class Entity(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, scale=True):
        super().__init__()
        base_image = pygame.image.load(
            resource_path(image_path)).convert_alpha()
        self.image = base_image
        if scale:
            self.image = pygame.transform.scale(
                base_image,
                (
                    base_image.get_width() * SCALE,
                    base_image.get_height() * SCALE
                )
            )

        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox_margin = ENTITY_HITBOX
        self.hitbox = self._compute_hitbox()
        self._hover_time = random.random() * 1000
        self._hover_amplitude = 0
        self._hover_speed = 0
        self._hover_enabled = False
        self._hover_origin = pygame.Vector2(self.rect.center)

    def enable_hover(self, amplitude=10, speed=1.0):
        self._hover_enabled = True
        self._hover_amplitude = amplitude
        self._hover_speed = speed
        self._hover_origin = pygame.Vector2(self.rect.center)

    def hover_around(self):
        if not self._hover_enabled:
            return

        self._hover_time += self._hover_speed

        dx = math.sin(self._hover_time * 0.02) * self._hover_amplitude
        dy = math.cos(self._hover_time * 0.017) * self._hover_amplitude

        self.rect.centerx = int(self._hover_origin.x + dx)
        self.rect.centery = int(self._hover_origin.y + dy)

        self.update_hitbox()

    def _compute_hitbox(self):
        pad_x = int(self.rect.width * self.hitbox_margin)
        pad_y = int(self.rect.height * self.hitbox_margin)
        return self.rect.inflate(-pad_x, -pad_y)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center
