import pygame

from scripts.engine.render import render_skills_tab, render_stats_tab, \
    render_settings_tab
from scripts.system.constants import *
from scripts.engine.sheet import SpriteSheet
from scripts.engine.skill_tab import Tab
from scripts.engine.utils import resource_path


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
            self.image = pygame.transform.scale(self.image,
                                                (self.image.get_width() * 2,
                                                 self.image.get_height() * 2))

        if hud_pos[0] == 'left':
            self.hud_x = hud_ratio['left'] + hud_padding + self.offset_x
        elif hud_pos[0] == 'right':
            self.hud_x = hud_ratio[
                             'right'] - hud_padding - self.image.get_width() + self.offset_x

        if hud_pos[1] == 'top':
            self.hud_y = hud_ratio['top'] + hud_padding + self.offset_y
        elif hud_pos[1] == 'bottom':
            self.hud_y = hud_ratio[
                             'bottom'] - hud_padding - self.image.get_height() + self.offset_y

        screen.blit(self.image, (self.hud_x, self.hud_y))


class Bar:
    def __init__(self, x, y, width, height, max_value, color=None,
                 background_color=pygame.Color(30, 30, 30),
                 border_color=pygame.Color(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.display_ratio = 0.0
        self.color = color if color else pygame.Color(255, 255, 255)
        self.background_color = background_color
        self.border_color = border_color
        self.smoothing_speed = 6.0

    def update(self, current_value, dt):
        target_ratio = max(0.0, min(current_value / self.max_value, 1.0))
        self.display_ratio += (
                                      target_ratio - self.display_ratio) * self.smoothing_speed * dt
        self.display_ratio = max(0.0, min(self.display_ratio, 1.0))

    def draw(self, screen, x=None, y=None):
        if x is not None:
            self.rect.x = x
        if y is not None:
            self.rect.y = y
        pygame.draw.rect(screen, self.background_color, self.rect)
        fill_height = int(self.rect.height * self.display_ratio)
        fill_rect = pygame.Rect(
            self.rect.x,
            self.rect.bottom - fill_height,
            self.rect.width,
            fill_height
        )
        pygame.draw.rect(screen, self.color, fill_rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 4)


class OverheatBar(Bar):
    def __init__(self, x, y, width, height, max_value):
        super().__init__(x, y, width, height, max_value)
        self.cool_color = pygame.Color(0, 150, 255)
        self.mid_color = pygame.Color(255, 200, 0)
        self.hot_color = pygame.Color(255, 60, 0)

    def _lerp_color(self, c1, c2, t):
        t = max(0.0, min(t, 1.0))
        return pygame.Color(
            int(c1.r + (c2.r - c1.r) * t),
            int(c1.g + (c2.g - c1.g) * t),
            int(c1.b + (c2.b - c1.b) * t)
        )

    def _get_color(self, ratio):
        ratio = max(0.0, min(ratio, 1.0))
        if ratio < 0.5:
            return self._lerp_color(self.cool_color, self.mid_color, ratio * 2)
        else:
            return self._lerp_color(self.mid_color, self.hot_color,
                                    (ratio - 0.5) * 2)

    def draw(self, screen, overheated=False, x=None, y=None):
        if x is not None:
            self.rect.x = x
        if y is not None:
            self.rect.y = y
        pygame.draw.rect(screen, self.background_color, self.rect)

        fill_height = int(self.rect.height * self.display_ratio)
        fill_rect = pygame.Rect(
            self.rect.x,
            self.rect.bottom - fill_height,
            self.rect.width,
            fill_height
        )

        color = self._get_color(self.display_ratio)

        if overheated and pygame.time.get_ticks() % 400 < 200:
            color = pygame.Color(255, 255, 255)

        pygame.draw.rect(screen, color, fill_rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 4)


class ShieldBar(Bar):
    def __init__(self, x, y, width, height, max_value):
        color = pygame.Color(0, 150, 255)
        super().__init__(x, y, width, height, max_value, color)


class XPBar(Bar):
    def __init__(self, x, y, width, height, max_value):
        color = pygame.Color(200, 100, 255)
        super().__init__(x, y, width, height, max_value, color)


class HUD:
    def __init__(self, game, screen_size, hud_ratio, game_font):
        self.hitpoints = Interface(
            resource_path("assets/ui/status.png"),
            0,
            *INTERFACE_HITPOINTS,
            hud_ratio, ['right', 'bottom'])

        self.guns = Interface(
            resource_path("assets/ui/guns.png"),
            0,
            INTERFACE_GUNS[0],
            INTERFACE_GUNS[1],
            hud_ratio, ['right', 'bottom'],
            INTERFACE_GUNS_COLS,
            GUNS_HUD_NUDGE)

        self.overheat_bar = OverheatBar(
            0, 0,
            width=INTERFACE_OVERHEAT_WIDTH,
            height=INTERFACE_OVERHEAT_HEIGHT,
            max_value=game.ship.overheat_limit)

        self.shield_bar = ShieldBar(
            0, 0,
            width=INTERFACE_OVERHEAT_WIDTH,
            height=INTERFACE_OVERHEAT_HEIGHT,
            max_value=game.ship.max_shield)

        self.xp_bar = XPBar(
            0, 0,
            width=INTERFACE_OVERHEAT_WIDTH,
            height=INTERFACE_OVERHEAT_HEIGHT,
            max_value=game.ship.xp_to_next_level)

        self.credits = game.ship.credits

        self.skill_tab = Tab(
            resource_path("assets/ui/skill_tab.png"),
            start_pos=(screen_size[0], SKILL_TAB_Y),
            content_renderer=render_skills_tab)

        self.stats_tab = Tab(
            resource_path("assets/ui/skill_tab.png"),
            start_pos=(screen_size[0] // 2 - self.skill_tab.rect.width // 2,
            screen_size[1]),
            content_renderer=render_stats_tab)

        self.settings_tab = Tab(
            resource_path("assets/ui/skill_tab.png"),
            start_pos=(screen_size[0] // 2 - self.skill_tab.rect.width // 2,
            screen_size[1]),
            content_renderer=render_settings_tab)

    def update(self, game, font, screen, hud_ratio, hud_padding):
        line_spacing = font.get_linesize()
        score_x, y = padded_pos(hud_ratio['left'], hud_ratio['top'], 'left',
                                'top', hud_padding)

        score_title_surf = font.render(game.local.t('game.score'), True,
                                       COLOR_WHITE)
        screen.blit(score_title_surf, [score_x, y])

        y += line_spacing
        score_value_surf = font.render(f"{int(game.state.score):06}", True,
                                       COLOR_WHITE)
        screen.blit(score_value_surf, [score_x, y])
        y += line_spacing

        credits_surf = font.render(f"${game.ship.credits:,.0f}", True,
                                   COLOR_LIGHT_ORANGE)
        screen.blit(credits_surf, [score_x, y])

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
            (self.hitpoints, game.ship.hitpoints, game.ship.max_hitpoints, True)
        ]

        for interface, value, max_value, reverse in interfaces:
            frame = value_to_frame(value, max_value, len(interface.frames),
                                   reverse)
            interface.update(game.ship, hud_ratio, ['right', 'bottom'],
                             frame, screen, hud_padding)

        self.overheat_bar.max_value = game.ship.overheat_limit
        self.shield_bar.max_value = game.ship.max_shield
        self.xp_bar.max_value = game.ship.xp_to_next_level

        self.overheat_bar.update(game.ship.heat, game.delta)
        self.shield_bar.update(game.ship.shield, game.delta)
        self.xp_bar.update(game.ship.xp, game.delta)

        bar_width = self.overheat_bar.rect.width
        bar_height = self.overheat_bar.rect.height

        bar_y = self.guns.hud_y

        overheat_x = (self.guns.hud_x + self.guns.image.get_width() + BAR_SPACING)
        shield_x = overheat_x + bar_width + BAR_SPACING
        xp_x = shield_x + bar_width + BAR_SPACING

        self.overheat_bar.draw(screen, game.ship.overheated,
                               x=overheat_x, y=bar_y)
        self.shield_bar.draw(screen, x=shield_x, y=bar_y)
        self.xp_bar.draw(screen, x=xp_x, y=bar_y)

        current_gun_frame = game.ship.gun_order.index(game.ship.gun)

        self.guns.update(game.ship, hud_ratio, ['right', 'bottom'],
                         current_gun_frame, screen, hud_padding)

        current_ammo = game.ship.guns_ammo[game.ship.gun]
        total_ammo = "inf" if game.ship.gun == "beam" else (
            game.ship.base_guns_ammo)[game.ship.gun]

        icon_left_x = self.guns.hud_x
        x_right_edge = icon_left_x - TEXT_PADDING

        gun_tag = SHIP_TAGS.get(game.ship.gun, game.ship.gun)
        gun_name = game.local.t(gun_tag)
        gun_name_surface = font.render(gun_name, True, COLOR_LIGHT_ORANGE)

        gun_name_x = x_right_edge - gun_name_surface.get_width()
        gun_name_y = self.guns.hud_y + GUN_LABEL_OFFSET
        screen.blit(gun_name_surface, [gun_name_x, gun_name_y])

        ammo_text = f"{current_ammo}/{total_ammo}"
        ammo_surface = font.render(ammo_text, True, COLOR_WHITE)
        ammo_x = x_right_edge - ammo_surface.get_width()
        ammo_y = gun_name_y + gun_name_surface.get_height() + LINE_SPACING
        screen.blit(ammo_surface, [ammo_x, ammo_y])

        wave_text = game.local.t('game.hud.wave',
                                 wave=game.state.real_phase_index + 1)
        wave_surface = font.render(wave_text, True, COLOR_WHITE)
        wave_x = score_x
        y += line_spacing
        wave_y = y
        screen.blit(wave_surface, [wave_x, wave_y])

        if game.state.sandbox_enabled:
            sandbox_text = f"SANDBOX: {game.state.sandbox_enemy_type}"
            sandbox_surf = font.render(sandbox_text, True, COLOR_LIGHT_ORANGE)
            y += line_spacing
            screen.blit(sandbox_surf, [score_x, y])

        self.skill_tab.update()
        self.stats_tab.update()
        self.settings_tab.update()
