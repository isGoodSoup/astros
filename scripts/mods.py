import math

import pygame

import scripts.assets as assets
from scripts.difficulty import DifficultyPool
from scripts.game import Game
from scripts.fonts import FontManager
from scripts.intro import Intro
from scripts.mixer import Mixer
from scripts.settings import SCALE, SHIP_FRAMES, COLOR_BLACK, \
    COLOR_LIGHT_ORANGE, FONT_DEFAULT_SIZE, TRAIT_CARD_SIZE, HEADER_FLOAT, \
    SPRITE_FLOAT, FPS, SHIP_SELECTION_OFFSET, FLIGHT_SPEED, ALPHA, \
    TOGGLE_ENABLE_INTRO
from scripts.shared import fade, joysticks
from scripts.traits import TraitOption, TraitGridSquare, TraitPool
from scripts.utils import render_fade

mixer = Mixer()

class Mods:
    def __init__(self, context, screen, screen_size, hud_ratio):
        fade.start("in")
        self.context = context
        self.local = context.local
        self.running = True
        self.screen_size = screen_size
        self.font = FontManager(None, FONT_DEFAULT_SIZE)
        self.preview_scale = SCALE//2
        self.ship_frames = SHIP_FRAMES
        self.ship_flying = False
        self.flight_speed = FLIGHT_SPEED
        self.flight_offset = 0
        self.fade_started = False

        self.ships = assets.SHIPS
        self.selected_ship_index = None
        self.current_ship_index = 0
        self.ship_previews = []
        self.ship_previews_large = []

        for sheet in self.ships:
            framew = sheet.sheet.get_width() // self.ship_frames
            frameh = sheet.sheet.get_height()
            idle_frame_index = 2

            preview = sheet.get_frame(idle_frame_index,
                cols=self.ship_frames).convert_alpha()

            preview = pygame.transform.scale(preview, (framew * SCALE,
                                                       frameh * SCALE))

            large_preview = pygame.transform.scale(preview,
                (preview.get_width() * self.preview_scale,
                 preview.get_height() * self.preview_scale))

            self.ship_previews.append(preview)
            self.ship_previews_large.append(large_preview)

        w, h = self.ship_previews[0].get_size()
        self.dim_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.dim_surface.fill((0, 0, 0, ALPHA))

    def run(self, clock, screen, screen_size, hud_ratio, crt):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.input(event, clock, screen, screen_size,
                           hud_ratio, crt)

            screen.fill(COLOR_BLACK)
            clock.tick(FPS)

            if self.ship_flying:
                self.flight_offset -= self.flight_speed

                if not self.fade_started:
                    fade.start("out")
                    self.fade_started = True

            self.draw(screen)
            alpha = render_fade(screen, screen_size)
            crt.render(screen)

            if self.ship_flying and self.fade_started and alpha >= 255:
                traits = TraitChoiceScreen(self.context, screen, screen_size, hud_ratio,
                    TraitPool(self.context)).run(clock, screen, screen_size,
                                           hud_ratio, crt)
                difficulties = Difficulties(self.context, screen, screen_size, hud_ratio,
                    DifficultyPool(self.context)).run(clock, screen, screen_size,
                                           hud_ratio, crt)
                selected_traits = traits.get_traits() if traits else []
                if TOGGLE_ENABLE_INTRO:
                    intro = Intro(self.context, screen, clock, crt).run()

                game = Game(self.context, screen, screen_size, crt, hud_ratio,
                            selected_traits, self.ships,
                            self.selected_ship_index)
                self.running = False
                game.run(clock, screen, screen_size, hud_ratio, crt)

    def input(self, event, clock, screen, screen_size, hud_ratio, crt):
        if self.ship_flying:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.current_ship_index = ((self.current_ship_index - 1)
                                           % len(self.ship_previews))
                mixer.play(5)

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.current_ship_index = ((self.current_ship_index + 1)
                                           % len(self.ship_previews))
                mixer.play(5)

            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.ship_flying = True
                self.selected_ship_index = self.current_ship_index
                mixer.play(4)

        if joysticks:
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.ship_flying = True
                    self.selected_ship_index = self.current_ship_index
                    mixer.play(4)

                if event.button == 5:
                    self.current_ship_index = ((self.current_ship_index + 1)
                                               % len(self.ship_previews))
                    mixer.play(5)

                if event.button == 4:
                    self.current_ship_index = ((self.current_ship_index - 1)
                                               % len(self.ship_previews))
                    mixer.play(5)

    def draw(self, screen):
        center_x = self.screen_size[0] // 2
        center_y = self.screen_size[1] // 2
        time = pygame.time.get_ticks()

        ship_float = 4 * math.sin(time * SPRITE_FLOAT)
        if self.ship_flying:
            ship_float += self.flight_offset

        current_preview = self.ship_previews_large[self.current_ship_index]
        rect = current_preview.get_rect(
            center=(center_x, center_y + int(ship_float)))
        screen.blit(current_preview, rect)

        offset = SHIP_SELECTION_OFFSET
        phase = math.pi / 2

        left_index = (self.current_ship_index - 1) % len(self.ship_previews)
        right_index = (self.current_ship_index + 1) % len(self.ship_previews)

        left_float = 2 * math.sin(time * SPRITE_FLOAT + phase)
        right_float = 2 * math.sin(time * SPRITE_FLOAT - phase)

        left_preview = self.ship_previews[left_index]
        right_preview = self.ship_previews[right_index]

        left_rect = left_preview.get_rect(center=(center_x - offset, center_y + int(left_float)))
        right_rect = right_preview.get_rect(center=(center_x + offset, center_y + int(right_float)))

        screen.blit(left_preview, left_rect)
        screen.blit(self.dim_surface, left_rect)

        screen.blit(right_preview, right_rect)
        screen.blit(self.dim_surface, right_rect)

        header_float = 4 * math.sin(time * HEADER_FLOAT)

        header = self.local.t('mods.header')
        header_surf = self.font.render(header, True, COLOR_LIGHT_ORANGE)
        header_rect = header_surf.get_rect(
            center=(center_x, 100 + int(header_float)))
        screen.blit(header_surf, header_rect)

class TraitChoiceScreen:
    def __init__(self, context, screen, screen_size, hud_ratio,
                 pool: TraitPool):
        self.context = context
        self.local = context.local
        self.screen = screen
        self.screen_size = screen_size

        self.pool = pool

        self.node = ChoiceNode(pool.roll(count=pool.length()), pick_count=1)
        self.font = FontManager(None, FONT_DEFAULT_SIZE).get_font()

        self.cards = [
            TraitGridSquare(opt, self.font)
            for opt in self.node.options
        ]

        self.index = 0
        self.exiting = False
        self.result = None
        self.fade_out_started = False
        fade.start('in')

    def run(self, clock, screen, screen_size, hud_ratio, crt):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                self.input(event)

            screen.fill(COLOR_BLACK)
            clock.tick(FPS)

            self.update()
            self.draw()

            if self.exiting and not self.fade_out_started:
                fade.start('out')
                self.fade_out_started = True

            alpha = render_fade(screen, screen_size)
            crt.render(screen)

            if self.fade_out_started and alpha >= 255:
                return self.result

    def update(self):
        for i, card in enumerate(self.cards):
            card.set_selected(i == self.index)

    def draw(self):
        cx = self.screen_size[0] // 2
        cy = self.screen_size[1] // 2
        time = pygame.time.get_ticks()

        spacing = TRAIT_CARD_SIZE + 50
        for i, card in enumerate(self.cards):
            x = cx + (i - (len(self.cards) - 1) / 2) * spacing
            card.draw(self.screen, (x, cy))

        header_float = 4 * math.sin(time * HEADER_FLOAT)

        header = self.local.t('traits.header')
        header_surf = self.font.render(header, True, COLOR_LIGHT_ORANGE)
        header_rect = header_surf.get_rect(
            center=(cx, 100 + int(header_float)))
        self.screen.blit(header_surf, header_rect)

    def input(self, event):
        if self.exiting:
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.index = (self.index - 1) % len(self.cards)
                mixer.play(5)

            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.index = (self.index + 1) % len(self.cards)
                mixer.play(5)

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.node.select(self.index)
                self.result = self.node.confirm()
                self.exiting = True
                mixer.play(4)

        if event.type == pygame.JOYHATMOTION:
            if event.hat == 0 and event.value == (-1, 0):
                self.index = (self.index - 1) % len(self.cards)
                mixer.play(5)

            if event.hat == 0 and event.value == (1, 0):
                self.index = (self.index + 1) % len(self.cards)
                mixer.play(5)

        if event.type == pygame.JOYBUTTONDOWN and event.button == 0:
            self.node.select(self.index)
            self.result = self.node.confirm()
            self.exiting = True
            mixer.play(4)

class ChoiceNode:
    def __init__(self, options, pick_count=1):
        self.options = [TraitOption(t) for t in options]
        self.pick_count = pick_count

        self.selected = []
        self.done = False

    def select(self, index):
        option = self.options[index]

        if option in self.selected:
            self.selected.remove(option)
            return

        if len(self.selected) < self.pick_count:
            self.selected.append(option)

    def confirm(self):
        if len(self.selected) == 0:
            return None

        self.done = True
        return ChoiceResult(self.selected)

class ChoiceResult:
    def __init__(self, selected_options):
        self.selected_options = selected_options

    def get_traits(self):
        return [opt.trait for opt in self.selected_options]

class Difficulties:
    def __init__(self, context, screen, screen_size, hud_ratio,
                 pool: DifficultyPool):
        fade.start('in')
        self.context = context
        self.local = context.local
        self.screen = screen
        self.screen_size = screen_size

        self.pool = pool
        self.options = pool.options

        self.font = FontManager(None, FONT_DEFAULT_SIZE).get_font()

        self.cards = [TraitGridSquare(opt, self.font)
            for opt in self.options]

        self.index = 0
        self.selected = None
        self.exiting = False

    def run(self, clock, screen, screen_size, hud_ratio, crt):
        while not self.exiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exiting = True

                self.input(event)

            screen.fill(COLOR_BLACK)
            clock.tick(FPS)

            self.render()

            alpha = render_fade(screen, screen_size)
            crt.render(screen)

        return self.selected.trait

    def input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.index = (self.index - 1) % len(self.options)
                mixer.play(5)

            elif event.key == pygame.K_RIGHT:
                self.index = (self.index + 1) % len(self.options)
                mixer.play(5)

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.selected = self.options[self.index]
                mixer.play(4)
                self.exiting = True
                fade.start('out')

        if event.type == pygame.JOYHATMOTION:
            if event.hat == 0 and event.value == (-1, 0):
                self.index = (self.index - 1) % len(self.options)
                mixer.play(5)

            if event.hat == 0 and event.value == (1, 0):
                self.index = (self.index + 1) % len(self.options)

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                self.selected = self.options[self.index]
                mixer.play(4)
                self.exiting = True
                fade.start('out')

    def render(self):
        cx = self.screen_size[0] // 2
        cy = self.screen_size[1] // 2
        time = pygame.time.get_ticks()

        header_float = 4 * math.sin(time * HEADER_FLOAT)
        header = self.local.t('game.difficulty.header')
        header_surf = self.font.render(header, True, COLOR_LIGHT_ORANGE)
        header_rect = header_surf.get_rect(
            center=(cx, 100 + int(header_float)))
        self.screen.blit(header_surf, header_rect)

        spacing = TRAIT_CARD_SIZE + 50

        for i, card in enumerate(self.cards):
            x = cx + (i - (len(self.cards) - 1) / 2) * spacing
            card.set_selected(i == self.index)
            card.draw(self.screen, (x, cy))

        alpha = render_fade(self.screen, self.screen_size)