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

    def update(self, ship, hud_ratio, hud_pos, frame, screen, hud_padding=0):
        frame = int(min(frame, len(self.frames) - 1))
        self.hud_x = hud_ratio[hud_pos[0]] - self.image.get_width() + self.offset_x
        self.hud_y = hud_ratio[hud_pos[1]] - self.image.get_height() + self.offset_y

        if hud_pos[0] == 'left':
            self.hud_x += hud_padding
        elif hud_pos[0] == 'right':
            self.hud_x -= hud_padding
        if hud_pos[1] == 'top':
            self.hud_y += hud_padding
        elif hud_pos[1] == 'bottom':
            self.hud_y -= hud_padding

        screen.blit(self.frames[frame], (self.hud_x, self.hud_y))

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
        self.credits = 0

        self.skill_tab = Tab("assets/ui/skill_tab.png",
            start_pos=(screen_size[0], 200), content_renderer=render_skills_tab)

        self.stats_tab = Tab("assets/ui/skill_tab.png",
            start_pos=(screen_size[0] // 2 - self.skill_tab.rect.width // 2,
                       screen_size[1]), content_renderer=render_stats_tab)

    def update(self, game, font, screen, hud_ratio, hud_padding):
        cr_x, cr_y = padded_pos(hud_ratio['left'], hud_ratio['top'], 'left',
                                'top', hud_padding)
        credits_text = font.render(f"{game.ship.credits} CRD", True, "YELLOW")
        screen.blit(credits_text, [cr_x, cr_y])

        score_lines = ["", "SCORE"]
        score_line_surfs = [font.render(line, True, "WHITE") for line in score_lines]
        score_value_surface = font.render(f"{int(game.state.score):06}", True, "WHITE")

        score_x = cr_x
        score_y = cr_y + credits_text.get_height() + 5
        screen.blit(score_value_surface, [score_x, score_y])

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

        def update_interface(interface, pos):
            interface.update(game.ship, hud_ratio, pos,
                             interface.frames.index(interface.image), screen,
                             hud_padding)

        update_interface(self.hitpoints, ['right', 'bottom'])
        update_interface(self.shield, ['right', 'bottom'])
        update_interface(self.xp, ['right', 'bottom'])
        update_interface(self.ammo, ['right', 'bottom'])

        self.skill_tab.update()
        self.stats_tab.update()