import pygame

from scripts.render import render_skills_tab, render_stats_tab
from scripts.sheet import SpriteSheet
from scripts.skill_tab import Tab


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

    def update(self, ship, hud_ratio, hud_pos, frame, screen):
        frame = int(min(frame, len(self.frames) - 1))
        self.hud_x = hud_ratio[hud_pos[0]] - self.image.get_width() + self.offset_x
        self.hud_y = hud_ratio[hud_pos[1]] - self.image.get_height() + self.offset_y
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

    def update(self, game, font, screen, hud_ratio):
        game.clock.stopwatch = font.render(f"{game.clock.hours:02}:{game.clock.minutes:02}"
                                      f":{game.clock.seconds:02}", True, "WHITE")
        screen.blit(game.clock.stopwatch,[hud_ratio['left'] + hud_ratio['width'] // 2 -
                     game.clock.stopwatch.get_width() // 2, hud_ratio['top']])

        score_text = f"{int(game.state.score):06}"
        high_score = f"{int(game.state.high_score):06}"
        score_surface = font.render(score_text, True, "WHITE")
        high_score_surface = font.render(high_score, True, "WHITE")

        line_spacing = 2

        score_lines = ["", "SCORE"]
        score_line_surfs = [font.render(line, True, "WHITE") for line in
                            score_lines]

        title_height = sum(
            s.get_height() for s in score_line_surfs) + line_spacing * (
                                   len(score_line_surfs) - 1)
        score_value_y = hud_ratio['top'] + title_height + 5

        screen.blit(score_surface, [hud_ratio['left'], score_value_y])

        y = score_value_y - 5
        for surf in reversed(score_line_surfs):
            y -= surf.get_height()
            screen.blit(surf, [hud_ratio['left'], y])
            y -= line_spacing

        high_lines = ["HIGH", "SCORE"]
        high_line_surfs = [font.render(line, True, "WHITE") for line in
                           high_lines]

        block_width = max(
            s.get_width() for s in high_line_surfs + [high_score_surface])
        x_pos = hud_ratio['right'] - block_width
        screen.blit(high_score_surface, [x_pos, score_value_y])

        y = score_value_y - 5
        for surf in reversed(high_line_surfs):
            y -= surf.get_height()
            screen.blit(surf, [x_pos, y])
            y -= line_spacing

        total_frames = len(self.hitpoints.frames) - 1
        if game.ship.hitpoints <= 0:
            hitpoints_frame = total_frames
        else:
            hitpoints_frame = (
                        total_frames - (game.ship.hitpoints * total_frames)
                        // game.ship.max_hitpoints)
            hitpoints_frame = max(0, min(hitpoints_frame, total_frames))
        self.hitpoints.update(game.ship, hud_ratio, ['right', 'bottom'],
                              hitpoints_frame, screen)

        shield_total_frames = len(self.shield.frames) - 1
        shield_frame = (shield_total_frames - (
                game.ship.shield * shield_total_frames)
                        // game.ship.max_shield)
        shield_frame = max(0, min(shield_total_frames, shield_frame))
        self.shield.update(game.ship, hud_ratio, ['right', 'bottom'],
                           shield_frame, screen)

        experience_total_frames = len(self.xp.frames) - 1
        xp_frame = (experience_total_frames - (
                experience_total_frames * game.ship.xp)
                    // game.ship.xp_to_next_level)
        self.xp.update(game.ship, hud_ratio, ['right', 'bottom'], xp_frame,
                       screen)

        ammo_total_frames = len(self.ammo.frames) - 1
        ammo_frame = (
                    ammo_total_frames - (game.ship.ammo * ammo_total_frames)
                    // game.ship.base_ammo)
        ammo_frame = max(0, min(ammo_total_frames, ammo_frame))
        self.ammo.update(game.ship, hud_ratio, ['right', 'bottom'], ammo_frame,
                         screen)

        self.skill_tab.update()
        self.stats_tab.update()