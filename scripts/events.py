import random

from scripts.celestial import BlackHole
from scripts.explode import Explosion
from scripts.shared import joysticks, controller
from scripts.shockwave import Shockwave

class Events:
    def nuke_event(self, center, game):
        game.shockwaves.append(Shockwave(center, max_radius=900, speed=40))
        game.explosions.add(Explosion(center[0], center[1],
                                      game.frame_big_explode))

        game.nuke_flash = 255
        game.screen_shake = 80
        if joysticks:
            controller.rumble(0.5, 1, 1000)

    def black_hole_event(self, game):
        x, y = (random.randint(0, game.screen_width),
               random.randint(0, game.screen_height))
        game.celestials.add(BlackHole(x, y))