import pygame

from scripts.constants import ENTITY_HITBOX, SCALE, SHIP_FRAMES


class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    @property
    def hitbox(self):
        w = int(self.rect.width * ENTITY_HITBOX)
        h = int(self.rect.height * ENTITY_HITBOX)

        box = pygame.Rect(0, 0, w, h)
        box.center = self.rect.center
        return box

class AnimatedEntity(Entity):
    def __init__(self, sheet, frame, frame_w, frame_h, x, y):
        image = sheet.get_image(frame, frame_w, frame_h, scale=SCALE, columns=SHIP_FRAMES)
        super().__init__(image, x, y)
        self.sheet = sheet