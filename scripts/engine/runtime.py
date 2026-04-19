import random
import pygame

def get_upgrade_position():
    info = pygame.display.Info()
    return (
        random.randint(0, info.current_w),
        random.randint(-200, -50)
    )

def get_alien_pos(x, y):
    info = pygame.display.Info()
    return info.current_w // 2 - x // 2, info.current_h // 2 - y // 2

def get_boss_pos():
    info = pygame.display.Info()
    return [info.current_w // 2 + random.randint(-200, 200), -500]

def get_ship_ember():
    return [255, random.randint(50, 150), 0]

def get_desc(rect):
    return pygame.Rect(rect.x + 50, rect.y + 300, rect.width - 100, 180)