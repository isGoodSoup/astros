import pygame

from scripts.render import render_skills_tab, render_stats_tab
from scripts.settings import (COLOR_WHITE, COLOR_LIGHT_ORANGE, SKILL_TAB_Y, \
                              INTERFACE_HITPOINTS, INTERFACE_SHIELD,
                              INTERFACE_SHIELD_COLS, \
                              INTERFACE_SHIELD_OFFSET, INTERFACE_XP,
                              INTERFACE_XP_OFFSET, INTERFACE_GUNS_COLS,
                              INTERFACE_GUNS_OFFSET, INTERFACE_GUNS,
                              INTERFACE_AMMO_OFFSET, INTERFACE_AMMO_COLS,
                              INTERFACE_AMMO, INTERFACE_XP_COLS)
from scripts.sheet import SpriteSheet
from scripts.skill_tab import Tab
from scripts.utils import resource_path


def padded_pos(base_x, base_y, alignment_x, alignment_y, hud_padding):
    if alignment_x == 'left':
        base_x += hud_padding
    elif alignment_x == 'right':
        base_x -= hud_padding
    if alignment_y == 'top':
        base_y += hud_padding
    elif alignment_y == 'bottom':
        base_y -= hud_padding
    return base_x, base_y

def value_to_frame(value, max_value, frame_count, reverse=False):
    if max_value <= 0:
        return 0
    ratio = max(0, min(value / max_value, 1))
    frame = int(ratio * (frame_count - 1))
    if reverse:
        frame = (frame_count - 1) - frame
    return frame

class Interface(pygame.sprite.Sprite):
    def __init__(self, path, frame, width, height, hud_ratio, hud_pos,
                 columns=29, offset=(0, 0), scale=4):
        super().__init__()
        if width <= 0 or height <= 0:
            raise ValueError(f"Invalid sprite dimensions: {width}x{height}")
        if columns <= 0:
            raise ValueError("Columns must be > 0")
        if scale <= 0:
            raise ValueError("Scale must be > 0")

        self.sprite_sheet = SpriteSheet(path)
        self.frames = [
            self.sprite_sheet.get_image(i, width, height, scale, columns)
            for i in range(columns)
        ]
        self.image = self.frames[frame]
        self.hud_x = hud_ratio[hud_pos[0]] - self.image.get_width()
        self.hud_y = hud_ratio[hud_pos[1]] - self.image.get_height()
        self.offset_x, self.offset_y = offset

    def update(self, ship, hud_ratio, hud_pos, frame, screen, hud_padding=0,
               scale=False):
        frame = int(min(frame, len(self.frames) - 1))
        self.image = self.frames[frame]
        if scale:
            self.image = pygame.transform.scale(self.image,(self.image.get_width() * 2,
                                                 self.image.get_height() * 2))

        if hud_pos[0] == 'left':
            self.hud_x = hud_ratio['left'] + hud_padding + self.offset_x
        elif hud_pos[0] == 'right':
            self.hud_x = hud_ratio['right'] - hud_padding - self.image.get_width() + self.offset_x

        if hud_pos[1] == 'top':
            self.hud_y = hud_ratio['top'] + hud_padding + self.offset_y
        elif hud_pos[1] == 'bottom':
            self.hud_y = hud_ratio['bottom'] - hud_padding - self.image.get_height() + self.offset_y

        screen.blit(self.image, (self.hud_x, self.hud_y))

class HUD:
    def __init__(self, game, screen_size, hud_ratio, game_font):
        self.hitpoints = Interface(resource_path("assets/ui/status.png"), 0,
                                   *INTERFACE_HITPOINTS,
                                   hud_ratio, ['right', 'bottom'])
        self.shield = Interface(resource_path("assets/ui/shield_bar.png"), 0,
                                INTERFACE_SHIELD[0], INTERFACE_SHIELD[1],
                                hud_ratio, ['right', 'bottom'],
                                INTERFACE_SHIELD_COLS, INTERFACE_SHIELD_OFFSET)
        self.xp = Interface(resource_path("assets/ui/xp.png"), 0,
                            INTERFACE_XP[0], INTERFACE_XP[1],
                            hud_ratio, ['right', 'bottom'],
                            INTERFACE_XP_COLS, INTERFACE_XP_OFFSET)
        self.ammo = Interface(resource_path("assets/ui/ammo.png"), 0,
                              INTERFACE_AMMO[0], INTERFACE_AMMO[1],
                              hud_ratio, ['right', 'bottom'],
                              INTERFACE_AMMO_COLS, INTERFACE_AMMO_OFFSET)
        self.guns = Interface(resource_path("assets/ui/guns.png"), 0,
                              INTERFACE_GUNS[0], INTERFACE_GUNS[1],
                              hud_ratio,['right', 'bottom'],
                              INTERFACE_GUNS_COLS, INTERFACE_GUNS_OFFSET)
        self.xp.image = self.xp.frames[len(self.xp.frames) - 1]

        self.guns_ammo = {
            "beam": game.ship.guns_ammo["beam"],
            "shotgun": game.ship.guns_ammo["shotgun"],
            "auto": game.ship.guns_ammo["auto"],
            "missile": game.ship.guns_ammo["missile"],
        }

        self.credits = 0

        self.skill_tab = Tab(resource_path("assets/ui/skill_tab.png"),
            start_pos=(screen_size[0], SKILL_TAB_Y), content_renderer=render_skills_tab)

        self.stats_tab = Tab(resource_path("assets/ui/skill_tab.png"),
            start_pos=(screen_size[0] // 2 - self.skill_tab.rect.width // 2,
                       screen_size[1]), content_renderer=render_stats_tab)

    def update(self, game, font, screen, hud_ratio, hud_padding):
        line_spacing = font.get_linesize()  # fixed per-font value from FontManager
        score_x, y = padded_pos(hud_ratio['left'], hud_ratio['top'], 'left',
                                'top', hud_padding)

        score_title_surf = font.render("SCORE", True, COLOR_WHITE)
        screen.blit(score_title_surf, [score_x, y])

        y += line_spacing
        score_value_surf = font.render(f"{int(game.state.score):06}", True,
                                       COLOR_WHITE)
        screen.blit(score_value_surf, [score_x, y])
        y += line_spacing

        credits_surf = font.render(f"${game.ship.credits:,}", True,
                                   COLOR_LIGHT_ORANGE)
        screen.blit(credits_surf, [score_x, y])
        y += line_spacing

        high_score_surface = font.render(f"{int(game.state.high_score):06}",
                                         True, COLOR_WHITE)
        hs_x, hs_y = padded_pos(hud_ratio['right'], hud_ratio['top'], 'right',
                                'top', hud_padding)
        hs_x -= high_score_surface.get_width()
        screen.blit(high_score_surface, [hs_x, hs_y])

        stopwatch_text = f"{game.clock.hours:02}:{game.clock.minutes:02}:{game.clock.seconds:02}"
        stopwatch_surface = font.render(stopwatch_text, True, COLOR_WHITE)
        sw_x = hud_ratio['left'] + hud_ratio[
            'width'] // 2 - stopwatch_surface.get_width() // 2
        sw_y = hud_ratio['top'] + hud_padding
        screen.blit(stopwatch_surface, [sw_x, sw_y])

        available_ammo = 0
        for ammo in game.ship.guns_ammo:
            available_ammo += game.ship.guns_ammo[ammo]

        current_gun_frame = game.ship.gun_order.index(game.ship.gun)
        interfaces = [
            (self.hitpoints, game.ship.hitpoints, game.ship.max_hitpoints, True),
            (self.shield, game.ship.shield, game.ship.max_shield, True),
            (self.xp, game.ship.xp, game.ship.xp_to_next_level, True),
            (self.ammo, available_ammo, game.ship.arsenal, True),
        ]

        for interface, value, max_value, reverse in interfaces:
            frame = value_to_frame(value, max_value, len(interface.frames), reverse)
            interface.update(game.ship, hud_ratio, ['right', 'bottom'], frame,
                             screen, hud_padding)

        current_gun_frame = game.ship.gun_order.index(game.ship.gun)
        self.guns.update(game.ship, hud_ratio, ['right', 'bottom'],
                         current_gun_frame, screen, hud_padding)

        current_ammo = game.ship.guns_ammo[game.ship.gun]
        total_ammo = game.ship.base_guns_ammo[game.ship.gun]

        guns_center_x = self.guns.hud_x + self.guns.image.get_width() // 2
        guns_bottom_y = self.guns.hud_y + self.guns.image.get_height()

        ammo_text = f"{current_ammo}/{total_ammo}"
        ammo_surface = font.render(ammo_text, True, COLOR_WHITE)
        ammo_x = guns_center_x - ammo_surface.get_width() // 2
        ammo_y = guns_bottom_y + 5
        screen.blit(ammo_surface, [ammo_x, ammo_y])

        self.skill_tab.update()
        self.stats_tab.update()