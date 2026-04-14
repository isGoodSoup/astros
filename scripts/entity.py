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
        self.z = 0

    def _compute_hitbox(self):
        pad_x = int(self.rect.width * self.hitbox_margin)
        pad_y = int(self.rect.height * self.hitbox_margin)
        return self.rect.inflate(-pad_x, -pad_y)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

class DepthEntity(Entity):
    def __init__(self, image, x, y, z, scale=True):
        super().__init__(image, x, y, scale)
        self.x = x
        self.y = y
        self.z = z
