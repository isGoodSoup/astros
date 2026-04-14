import pygame

from scripts.constants import ENTITY_HITBOX, SCALE
from scripts.utils import resource_path


class Entity(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y):
        super().__init__()
        self.image = pygame.image.load(
            resource_path(image_path)).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.image = pygame.transform.scale(self.image, [self.rect.width *
                                                        SCALE, self.rect.height * SCALE])

        self.hitbox_margin = ENTITY_HITBOX
        self.hitbox = self._compute_hitbox()

    def _compute_hitbox(self):
        return self.rect.inflate(
            -self.rect.width * self.hitbox_margin,
            -self.rect.height * self.hitbox_margin
        )

    def update_hitbox(self):
        self.hitbox.center = self.rect.center
