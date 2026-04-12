import random

import pygame

import scripts.assets as assets
from scripts.settings import *
from scripts.ship import Ship


class SpriteManager:
    def __init__(self, game):
        self.celestials = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.bosses = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.upgrades = pygame.sprite.Group()
        self.floating_numbers = pygame.sprite.Group()
        self.fleets = []
        self.particles = []
        self.shockwaves = []

        self.ship_frames = SHIP_FRAMES
        self.explosion_frames = EXPLOSION_FRAMES
        self.explosion_sheet = assets.EXPLOSION_SHEET
        self.megaexplosion_sheet = assets.MEGAEXPLOSION_SHEET
        self.ship_alive = True

        self.ship_sprite = game.ships
        self.selected_sheet = self.ship_sprite[game.ship_index]
        self.ship_frames = SHIP_FRAMES
        self.frame = 0

        self.anim_frame_base = 0
        self.anim_frame_overlay = 0
        self.anim_index_left = 0
        self.anim_index_right = 0
        self.cooldown_base = ANIM_COOLDOWN_BASE
        self.cooldown_overlay = ANIM_COOLDOWN_OVERLAY

        self.last_update_base = self.last_update_overlay = (
            self).last_update = self.last_update_left = (
            self).last_update_right = self.last_time = pygame.time.get_ticks()
        self.last_direction = self.direction_set = None

        self.frames = []
        self.framew = self.selected_sheet.sheet.get_width() // self.ship_frames
        self.frameh = self.selected_sheet.sheet.get_height()

        self.ship = self.create_ship()
        self.ship.spawnpoint(game.screen_size, self.framew)

        for i in range(self.ship_frames):
            img = self.selected_sheet.get_image(i, self.framew, self.frameh,scale=SCALE,
                                                columns=self.ship_frames)
            self.frames.append(img)

        self.left_frames_movement = self.frames[0:2]
        self.frame_idle = self.frames[2]
        self.right_frames_movement = self.frames[3:5]
        self.frames_flying = self.frames[5:9]
        self.base = self.frame_idle

        framew = self.explosion_sheet.sheet.get_width() // self.explosion_frames
        frameh = self.explosion_sheet.sheet.get_height()

        self.frame_explode = [
            self.explosion_sheet.get_image(i, framew, frameh, scale=SCALE,
                columns=self.explosion_frames) for i in range(self.explosion_frames)
        ]

        framew = self.megaexplosion_sheet.sheet.get_width() // 4
        frameh = self.megaexplosion_sheet.sheet.get_height()

        self.frame_big_explode = [
            self.megaexplosion_sheet.get_image(i, framew, frameh,
                scale=SCALE * 2, columns=4) for i in range(4)
        ]

        self.stars = [[random.randint(0, game.screen_size[0]),
                       random.randint(0, game.screen_size[1]),
                       random.randint(1, 3)] for _ in range(STAR_COUNT)]

        self.boss_invisible_start = pygame.time.get_ticks()
        self.boss_invisible_duration = BOSS_INVISIBLE_DURATION
        self.alien_delay = pygame.time.get_ticks() + ALIEN_INITIAL_DELAY

    def create_ship(self):
        return Ship(self.selected_sheet, 0, 0, self.frame, self.framew, self.frameh,
             columns=self.ship_frames)