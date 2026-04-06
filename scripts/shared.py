import pygame as pg
from scripts.fade import Fade

pg.init()
pg.joystick.init()
joysticks = [pg.joystick.Joystick(i) for i in range(pg.joystick.get_count())]
for j in joysticks:
    j.init()

controller = joysticks[0] if joysticks else None

if controller and hasattr(controller, "rumble"):
    print("Rumbling for 2 seconds!")
    controller.rumble(1.0, 1.0, 2000)
else:
    print("No rumble support detected.")

fade = Fade()