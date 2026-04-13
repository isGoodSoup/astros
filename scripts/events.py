import random

import pygame

from scripts.celestial import BlackHole
from scripts.explode import Explosion
from scripts.settings import (HIGH_RUMBLE_MS, SHOCKWAVE_SPEED, SHOCKWAVE_RADIUS, \
                              SCREEN_SHAKE, ALIEN_SHOT_TIMER_MS)
from scripts.shared import joysticks, controller
from scripts.shockwave import Shockwave

class Events:
    def __init__(self):
        self.ALIENLASER = pygame.USEREVENT + 1
        pygame.time.set_timer(self.ALIENLASER, ALIEN_SHOT_TIMER_MS)

        self.MUSIC_END = pygame.USEREVENT + 2
        pygame.mixer.music.set_endevent(self.MUSIC_END)

    def nuke_event(self, center, game):
        game.sprites.shockwaves.append(Shockwave(center, max_radius=SHOCKWAVE_RADIUS,
                                         speed=SHOCKWAVE_SPEED))
        game.sprites.explosions.add(Explosion(center[0], center[1],
                                      game.sprites.frame_big_explode))

        game.screen_shake = SCREEN_SHAKE + 30
        if joysticks:
            controller.rumble(0.5, 1, HIGH_RUMBLE_MS)

    def black_hole_event(self, game):
        x, y = (random.randint(0, game.screen_size[0]),
               random.randint(0, game.screen_size[1]))
        game.sprites.celestials.add(BlackHole(game, x, y))