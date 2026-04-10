import random

from scripts.celestial import BlackHole
from scripts.explode import Explosion
from scripts.settings import (HIGH_RUMBLE_MS, SHOCKWAVE_SPEED, SHOCKWAVE_RADIUS, \
    SCREEN_SHAKE)
from scripts.shared import joysticks, controller
from scripts.shockwave import Shockwave

class Events:
    def nuke_event(self, center, game):
        game.shockwaves.append(Shockwave(center, max_radius=SHOCKWAVE_RADIUS,
                                         speed=SHOCKWAVE_SPEED))
        game.explosions.add(Explosion(center[0], center[1],
                                      game.frame_big_explode))

        game.nuke_flash = 255
        game.screen_shake = SCREEN_SHAKE + 30
        if joysticks:
            controller.rumble(0.5, 1, HIGH_RUMBLE_MS)

    def black_hole_event(self, game):
        x, y = (random.randint(0, game.screen_size[0]),
               random.randint(0, game.screen_size[1]))
        game.celestials.add(BlackHole(x, y))