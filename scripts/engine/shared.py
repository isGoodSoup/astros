import pygame

from scripts.engine.fade import Fade

pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for j in joysticks:
    j.init()

controller = joysticks[0] if joysticks else None

fade = Fade()