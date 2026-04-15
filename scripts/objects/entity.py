import pygame

from scripts.system.constants import ENTITY_HITBOX, SCALE, SHIP_FRAMES


class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))

    @property
    def hitbox(self):
        return self.rect.inflate(int(self.rect.width * ENTITY_HITBOX),
                                 int(self.rect.height * ENTITY_HITBOX))


class AnimatedEntity(Entity):
    def __init__(self, sheet, frame, frame_w, frame_h, x, y):
        image = sheet.get_image(frame, frame_w, frame_h, scale=SCALE,
                                columns=SHIP_FRAMES)
        super().__init__(image, x, y)
        self.sheet = sheet
