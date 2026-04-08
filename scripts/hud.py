import pygame

from scripts.render import render_skills_tab, render_stats_tab
from scripts.sheet import SpriteSheet
from scripts.skill_tab import Tab

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
        self.sprite_sheet = SpriteSheet(path)
        self.frames = [self.sprite_sheet.get_image(i, width, height, scale, columns)
            for i in range(columns)]
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
        self.hitpoints = Interface("assets/ui/status.png", 0, 40, 40,
                                   hud_ratio, ['right', 'bottom'])
        self.shield = Interface("assets/ui/shield_bar.png", 0, 40, 17,
                                hud_ratio, ['right', 'bottom'], 33, [0, -150])
        self.xp = Interface("assets/ui/xp.png", -1, 40, 17,
                            hud_ratio, ['right', 'bottom'], 33, [0, -175])
        self.ammo = Interface("assets/ui/ammo.png", 0, 11, 40,
                              hud_ratio, ['right', 'bottom'], 35, [-160, 0])
        self.guns = Interface("assets/ui/guns.png", 0, 32, 32, hud_ratio,
                              ['right', 'bottom'], 3, [-210, -20])
        self.credits = 0

        self.skill_tab = Tab("assets/ui/skill_tab.png",
            start_pos=(screen_size[0], 200), content_renderer=render_skills_tab)

        self.stats_tab = Tab("assets/ui/skill_tab.png",
            start_pos=(screen_size[0] // 2 - self.skill_tab.rect.width // 2,
                       screen_size[1]), content_renderer=render_stats_tab)

    def update(self, game, font, screen, hud_ratio, hud_padding):
        score_x, score_y = padded_pos(hud_ratio['left'], hud_ratio['top'],
                                      'left', 'top', hud_padding)

        score_value_surface = font.render(f"{int(game.state.score):06}", True,
                                          "WHITE")
        screen.blit(score_value_surface, [score_x, score_y])

        score_lines = ["", "SCORE"]
        score_line_surfs = [font.render(line, True, "WHITE") for line in
                            score_lines]

        y = score_y - 5
        for surf in reversed(score_line_surfs):
            y -= surf.get_height()
            screen.blit(surf, [score_x, y])
            y -= 2

        credits_text = font.render(f"${game.ship.credits:,}", True, (255, 210, 0))
        credits_y = score_y + score_value_surface.get_height() + 5
        screen.blit(credits_text, [score_x, credits_y])

        y = score_y - 5
        for surf in reversed(score_line_surfs):
            y -= surf.get_height()
            screen.blit(surf, [score_x, y])
            y -= 2

        high_score_surface = font.render(f"{int(game.state.high_score):06}",
                                         True, "WHITE")
        hs_x, hs_y = padded_pos(hud_ratio['right'], hud_ratio['top'], 'right',
                                'top', hud_padding)
        hs_x -= high_score_surface.get_width()
        screen.blit(high_score_surface, [hs_x, hs_y])

        stopwatch_text = f"{game.clock.hours:02}:{game.clock.minutes:02}:{game.clock.seconds:02}"
        stopwatch_surface = font.render(stopwatch_text, True, "WHITE")
        sw_x = hud_ratio['left'] + hud_ratio[
            'width'] // 2 - stopwatch_surface.get_width() // 2
        sw_y = hud_ratio['top'] + hud_padding
        screen.blit(stopwatch_surface, [sw_x, sw_y])

        current_gun_frame = game.ship.gun_order.index(game.ship.gun)
        interfaces = [
            (self.hitpoints, game.ship.hitpoints, game.ship.max_hitpoints, True),
            (self.shield, game.ship.shield, game.ship.max_shield, True),
            (self.xp, game.ship.xp, game.ship.xp_to_next_level, True),
            (self.ammo, game.ship.ammo, game.ship.base_ammo, True),
        ]

        for interface, value, max_value, reverse in interfaces:
            frame = value_to_frame(value, max_value, len(interface.frames), reverse)
            interface.update(game.ship, hud_ratio, ['right', 'bottom'], frame,
                             screen, hud_padding)

        current_gun_frame = game.ship.gun_order.index(game.ship.gun)
        self.guns.update(game.ship, hud_ratio, ['right', 'bottom'],
                         current_gun_frame, screen, hud_padding)

        self.skill_tab.update()
        self.stats_tab.update()