import pygame

from scripts.engine.utils import colour
from scripts.system.constants import ENTITY_HITBOX, SCALE, SHIP_FRAMES, COLOR_WHITE


class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hit_flash_timer = 0
        self.hit_flash_duration = 8

    def trigger_hit_flash(self):
        self.hit_flash_timer = self.hit_flash_duration

    def update_hit_flash(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            if self.hit_flash_timer > self.hit_flash_duration - 2:
                self.image = colour(self.original_image, COLOR_WHITE)
            elif (self.hit_flash_timer // 2) % 2 == 0:
                self.image = colour(self.original_image, COLOR_WHITE)
            else:
                self.image = self.original_image
        else:
            self.image = self.original_image

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
