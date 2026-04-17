import pygame
from scripts.engine.sheet import SpriteSheet
from scripts.engine.utils import resource_path

ASTEROID_SPRITES = None
SHIPS = None
CURSOR = None
LOGO = None
ICON = None
STATUS = None
GUNS = None
GUNS_2 = None
EXPLOSION_SHEET = None
MEGAEXPLOSION_SHEET = None
OVERLAY_CONTROLLER = None
OVERLAY_KEYBOARD = None
MARKET_AMMO = None
MARKET_REPAIRS = None

def load_assets():
    global ASTEROID_SPRITES, SHIPS
    global CURSOR, LOGO, ICON, STATUS, GUNS, GUNS_2
    global EXPLOSION_SHEET, MEGAEXPLOSION_SHEET
    global OVERLAY_CONTROLLER, OVERLAY_KEYBOARD
    global MARKET_AMMO, MARKET_REPAIRS

    ASTEROID_SPRITES = [
        pygame.image.load(
            resource_path(f"assets/asteroids/asteroid_{i}.png")
        ).convert_alpha()
        for i in range(1, 8)
    ]

    SHIPS = tuple([
        SpriteSheet(resource_path("assets/ship.png")),
        SpriteSheet(resource_path("assets/ship_v2.png")),
        SpriteSheet(resource_path("assets/ship_v3.png")),
        SpriteSheet(resource_path("assets/ship_v4.png")),
        SpriteSheet(resource_path("assets/ship_v5.png")),
    ])

    CURSOR = pygame.image.load(resource_path("assets/ui/crosshair.png")).convert_alpha()
    LOGO = pygame.image.load(resource_path("assets/ui/logo.png")).convert_alpha()
    ICON = pygame.image.load(resource_path("assets/ui/icon.png")).convert_alpha()
    STATUS = SpriteSheet(resource_path("assets/ui/status.png"))
    GUNS = SpriteSheet(resource_path("assets/ui/guns.png"))
    GUNS_2 = SpriteSheet(resource_path("assets/ui/guns_2.png"))

    EXPLOSION_SHEET = SpriteSheet(resource_path("assets/explosion.png"))
    MEGAEXPLOSION_SHEET = SpriteSheet(resource_path("assets/explosion_charge.png"))

    OVERLAY_CONTROLLER = pygame.image.load(resource_path(
        "assets/ui/overlay_controller.png")).convert_alpha()

    OVERLAY_KEYBOARD = pygame.image.load(resource_path(
        "assets/ui/overlay_keyboard.png")).convert_alpha()

    MARKET_AMMO = pygame.image.load(resource_path(
        "assets/obj/bullet.png")).convert_alpha()
    MARKET_REPAIRS = pygame.image.load(resource_path("assets/obj/repairs.png")).convert_alpha()