import pygame

from scripts.settings import SHIP_HITBOX


class Alien(pygame.sprite.Sprite):
    def __init__(self, game, fleet, x, y, color):
        super().__init__()
        self.fleet = fleet
        self.game = game
        self.ship = game.ship
        self.image = pygame.image.load(f"assets/aliens/{color}.png")
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(self.rect * SHIP_HITBOX)
        self.shot_cooldown = 400

def spawn_fleet():
    pass