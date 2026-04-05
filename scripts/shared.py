import pygame as pg

pg.joystick.init()
joysticks = [pg.joystick.Joystick(i) for i in range(pg.joystick.get_count())]
for j in joysticks:
    j.init()

controller = joysticks[0] if joysticks else None
from scripts.fade import Fade
fade = Fade()