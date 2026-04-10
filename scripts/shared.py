import pygame

from scripts.fade import Fade
from scripts.settings import HIGH_RUMBLE_MS

pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for j in joysticks:
    j.init()

controller = joysticks[0] if joysticks else None

if controller and hasattr(controller, "rumble"):
    print("Rumbling for 2 seconds!")
    controller.rumble(1.0, 1.0, HIGH_RUMBLE_MS*2)
else:
    print("No rumble support detected.")

fade = Fade()