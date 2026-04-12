import random
import pygame

def get_upgrade_position():
    info = pygame.display.Info()
    return (
        random.randint(0, info.current_w),
        random.randint(-200, -50)
    )

def get_boss_pos():
    info = pygame.display.Info()
    return [info.current_w // 2 + random.randint(-200, 200), 350]

def get_ship_ember():
    return [255, random.randint(50, 150), 0]