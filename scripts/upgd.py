import random

import pygame

from scripts.soundlib import sounds

upgrades = ['power_up', 'shield', 'ammo']
def get_upgrade():
    return random.choice(upgrades)

class Upgrade(pygame.sprite.Sprite):
    def __init__(self, path, x, y, scale=4, upgrade_type="power_up"):
        super().__init__()
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image,(self.image.get_width() * scale,
                                                        self.image.get_height() * scale))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.copy()
        self.type = upgrade_type
        self.speed = 6
        self.x, self.y = x, y

    def update(self):
        self.y += self.speed
        self.rect.topleft = (self.x, self.y)
        self.hitbox.topleft = self.rect.topleft
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

    def apply(self, ship):
        now = pygame.time.get_ticks()

        if self.type == "power_up":
            if not hasattr(ship, "power_ups"):
                ship.power_ups = []
            ship.power_ups.append(now + 10_000)

        elif self.type == "shield":
            ship.shield_regen_active = True
            ship.shield_regen_end = now + 30_000
            ship.shield_regen_rate = int(ship.max_shield * 0.15)

        elif self.type == "ammo":
            for ammo in ship.guns_ammo:
                ship.guns_ammo[ammo] += 10

        sounds[2].play()