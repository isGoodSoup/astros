import pygame
from scripts.sheet import SpriteSheet

ASTEROID_SPRITES = None
SHIPS = None
CURSOR = None
LOGO = None
ICON = None
EXPLOSION_SHEET = None
MEGAEXPLOSION_SHEET = None


def load_assets():
    global ASTEROID_SPRITES, SHIPS
    global CURSOR, LOGO, ICON
    global EXPLOSION_SHEET, MEGAEXPLOSION_SHEET

    ASTEROID_SPRITES = [
        pygame.image.load(f"assets/asteroids/asteroid_{i}.png").convert_alpha()
        for i in range(1, 8)
    ]

    SHIPS = [
        SpriteSheet("assets/ship.png"),
        SpriteSheet("assets/ship_v2.png"),
        SpriteSheet("assets/ship_v3.png"),
    ]

    CURSOR = pygame.image.load("assets/ui/crosshair.png").convert_alpha()
    LOGO = pygame.image.load("assets/ui/logo.png").convert_alpha()
    ICON = pygame.image.load("assets/ui/icon.png").convert_alpha()

    EXPLOSION_SHEET = SpriteSheet("assets/explosion.png")
    MEGAEXPLOSION_SHEET = SpriteSheet("assets/explosion_charge.png")