import pygame

import scripts.assets as assets
import scripts.game as g
from scripts.game_over import game_lost
from scripts.lang import LANGS
from scripts.runtime import get_desc
from scripts.settings import *
from scripts.shared import joysticks, controller
from scripts.utils import render_fade
from scripts.utils import wrap_text

def render_frame(game, screen, font, hud_padding):
    now = pygame.time.get_ticks()

    boss_invisible = (
            hasattr(game, "boss_invisible_start") and
            now - game.sprites.boss_invisible_start <
            game.sprites.boss_invisible_duration
    )

    for i in game.sprites.stars:
        pygame.draw.circle(screen, COLOR_WHITE, (int(i[0]), int(i[1])), i[2])

    game.sprites.celestials.draw(screen)
    if game.state.phase_index in ASTEROID_PHASES:
        game.sprites.asteroids.draw(screen)

    if len(game.sprites.aliens) > 0:
        game.sprites.aliens.draw(screen)

    if not boss_invisible:
        game.sprites.bosses.draw(screen)

    game.sprites.projectiles.draw(screen)
    game.sprites.enemy_projectiles.draw(screen)
    game.sprites.upgrades.draw(screen)
    game.sprites.floating_numbers.draw(screen)

    for particle in game.sprites.particles:
        particle.draw(screen)

    img = game.sprites.base.copy()

    overlay_index = game.sprites.anim_frame_overlay % len(game.sprites.frames_flying)
    overlay_frame = game.sprites.frames_flying[overlay_index]
    img.blit(overlay_frame, (0, 0))

    if game.state.debugging:
        for i in game.sprites.asteroids:
            pygame.draw.rect(screen, COLOR_RED, i.hitbox, 2)

        for a in game.sprites.aliens:
            pygame.draw.rect(screen, COLOR_RED, a.rect, 2)

        for u in game.sprites.upgrades:
            pygame.draw.rect(screen, COLOR_GREEN, u.rect, 2)

        for p in game.sprites.projectiles:
            pygame.draw.rect(screen, COLOR_BLUE, p.rect, 2)

        for b in game.sprites.bosses:
            pygame.draw.rect(screen, COLOR_RED, b.rect, 2)

    if game.sprites.ship_alive:
        game.ship.rect.topleft = (game.ship.rect.x, game.ship.rect.y)
        screen.blit(img, game.ship.rect)
        if game.state.debugging:
            pygame.draw.rect(screen, COLOR_RED, game.ship.hitbox, 2)

    game.sprites.explosions.draw(screen)

    if game.hud.skill_tab.active and game.state.current_phase_options:
        cursor_pos = game.input.cursor_pos if joysticks else pygame.mouse.get_pos()
        game.input.selected_skill  = None

        for skill in game.state.current_phase_options:
            if skill.is_hovered(cursor_pos):
                game.input.selected_skill  = skill
                break

        mouse_pressed = pygame.mouse.get_pressed()[0]
        if mouse_pressed and game.input.selected_skill:
            game.skills.unlock_or_upgrade(game.input.selected_skill , game.ship)
            if game.input.selected_skill .unlocked and game.input.selected_skill  not in game.ship.skills:
                game.ship.add_skill(game.input.selected_skill )
            game.hud.skill_tab.close()


    render_waves(game, screen)

    game.hud.stats_tab.render(game, screen, font, hud_padding)
    game.hud.skill_tab.render(game, screen, font, hud_padding)

    if TOGGLE_TUTORIAL:
        game.tutorial.render(screen, font)

    if game.state.pause and (not game.hud.skill_tab.active or not
            game.hud.stats_tab.active):
        pause_text = g.local.t('game.pause')
        pause = game.font.render(pause_text, True, COLOR_WHITE)
        surf = None
        if game.state.can_show_controls:
            surf = assets.OVERLAY_CONTROLLER if (game.input.mode ==
                INPUT_CONTROLLER) else assets.OVERLAY_KEYBOARD

            surf = pygame.transform.scale(surf, (surf.get_width() * SCALE,
                                                 surf.get_height() * SCALE))

        dim_surface = pygame.Surface(game.screen_size)
        dim_surface.fill((0, 0, 0))
        dim_surface.set_alpha(ALPHA)

        if not game.hud.skill_tab.active:
            screen.blit(dim_surface, (0, 0))
            if not game.hud.settings_tab.active:
                if game.state.can_show_controls:
                    screen.blit(surf, [game.screen_size[0]//2 - surf.get_width()//2,
                                       game.screen_size[1]//2 - surf.get_height()//2])
                screen.blit(pause, [game.screen_size[0]//2 - pause.get_width()//2, PAUSED_TEXT_Y])

        game.hud.settings_tab.render(game, screen, font, hud_padding)

def render_skills_tab(game, screen, rect, game_font):
    title_text, perks = g.local.t('game.victory'), g.local.t("game.hud.perks",
                                                         perks=game.ship.perk_points)
    title = game_font.render(title_text, True, COLOR_WHITE)
    perk_points = game_font.render(perks, True, COLOR_WHITE)
    padding, offset = SKILL_TAB_OFFSETS

    screen.blit(title, (rect.x + SKTAB_HEADER_OFFSET + offset, rect.y + padding))
    screen.blit(perk_points, (rect.x + SKTAB_HEADER_OFFSET + offset, rect.y + padding + SKILL_TAB_PADDING))

    cursor_pos = game.input.cursor_pos if game.input.mode == INPUT_CONTROLLER \
        else pygame.mouse.get_pos()

    for i, (skill, pos) in enumerate(zip(game.state.current_phase_options,
                                         SKILL_TAB_GRID)):
        skill.pos = (rect.x + pos[0] + offset, rect.y + pos[1])
        skill.rect.topleft = skill.pos

        mouse_hovered = skill.rect.collidepoint(cursor_pos)
        controller_hovered = (i == game.input.selected_skill_index)
        skill.hovered = mouse_hovered or controller_hovered

        if skill.hovered:
            game.input.selected_skill = skill
            skill.show_description = True
        else:
            skill.show_description = False

        frame = pygame.transform.scale(skill.current_frame(), (64, 64))

        if skill.hovered and skill.description:
            desc_rect = get_desc(rect)
            description_surface = game_font.render(skill.description, True,COLOR_WHITE)
            description_rect = description_surface.get_rect(center=desc_rect.center)

            text = g.local.t(skill.description_key)
            lines = wrap_text(text, game_font.get_font(), desc_rect.width)

            screen.set_clip(desc_rect)

            y = desc_rect.top
            line_height = game_font.get_linesize()

            for line in lines:
                text_surface = game_font.render(line, True, COLOR_WHITE)
                screen.blit(text_surface, (desc_rect.x, y))
                y += line_height

            screen.set_clip(None)

        screen.blit(frame, skill.rect)
        screen.blit(skill.icon_image, skill.rect)

def render_stats_tab(game, screen, rect, game_font):
    available_ammo = 0
    for ammo in game.ship.guns_ammo:
        available_ammo += game.ship.guns_ammo[ammo]

    stats = [
        g.local.t("game.hud.hitpoints", hp=int(game.ship.hitpoints),
                max_hp=int(game.ship.max_hitpoints)),
        g.local.t("game.hud.shield", shield=int(game.ship.shield),
                max_shield=int(game.ship.max_shield)),
        g.local.t("game.hud.ammo", ammo=int(available_ammo),
                max_ammo=int(game.ship.arsenal)),
        g.local.t("game.hud.level", level=int(game.ship.level)),
        g.local.t("game.hud.xp", xp=int(game.ship.xp),
                xp_to_next_level=int(game.ship.xp_to_next_level)),
        g.local.t("game.hud.crit_chance",
                crit_chance=int(game.ship.crit_chance * 100)),
        g.local.t("game.hud.crit_multiplier",
                crit_multiplier=int(game.ship.crit_multiplier)),
    ]

    y_offset = STAT_Y_OFFSET
    for stat in stats:
        text_surface = game_font.render(stat, True, COLOR_WHITE)
        screen.blit(text_surface, (rect.x + 40, rect.y + y_offset))
        y_offset = next_row(y_offset)

def render_settings_tab(game, screen, rect, game_font):
    header_surface = game_font.render(g.local.t('game.settings.header'), True,
                                      COLOR_WHITE)
    header_rect = header_surface.get_rect()
    header_rect.topleft = (rect.x + SETTINGS_X_OFFSET, rect.y +
                           SETTINGS_Y_OFFSET)
    screen.blit(header_surface, header_rect)

    label_x = header_rect.left - header_rect.width // 2 - SETTINGS_COL_OFFSET
    slider_x = label_x + SETTINGS_COL_OFFSET * 2
    y = header_rect.bottom + SETTINGS_LINESPACE

    bar_width = SETTINGS_VOLUME_WIDTH
    bar_height = SETTINGS_VOLUME_HEIGHT

    for i, setting in enumerate(SETTINGS_DEFINITION):
        label = g.local.t(setting["label"])
        color = COLOR_GREEN if i == game.input.selected_setting_index else COLOR_WHITE

        label_surface = game_font.render(label, True, color)
        label_rect = label_surface.get_rect()
        label_rect.topleft = (label_x, y)

        screen.blit(label_surface, label_rect)

        if setting["type"] == "slider":
            value = getattr(getattr(game, setting["target"]), setting["key"])
            fill_width = int(bar_width * value)
            bar_y = label_rect.centery - bar_height // 2
            pygame.draw.rect(screen, COLOR_BLACK,
                             (slider_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, COLOR_WHITE,
                             (slider_x, bar_y, fill_width, bar_height))

        elif setting["type"] == "toggle":
            state = getattr(getattr(game, setting["target"]), setting["key"])
            toggle_text = "ON" if state else "OFF"
            toggle_surface = game_font.render(toggle_text, True, color)
            screen.blit(toggle_surface, (slider_x, y))

        elif setting["type"] == "lang":
            state = getattr(getattr(game, setting["target"]), setting["key"])
            option_text = LANGS.get(state, str(state))
            option_surface = game_font.render(option_text, True, color)
            screen.blit(option_surface, (slider_x, y))

        y = next_row(y, 40)

def next_row(y, spacing=SETTINGS_LINESPACE):
    return y + spacing

def render_waves(game, screen):
    for wave in game.sprites.shockwaves:
        alpha = max(0, 255 * (1 - wave.radius / wave.max_radius))
        surf = pygame.Surface((wave.radius * 2, wave.radius * 2),
                              pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, int(alpha)),
            (wave.radius, wave.radius), int(wave.radius), 6)

        screen.blit(surf,
            (wave.x - wave.radius, wave.y - wave.radius))

class RenderScreen:
    def draw(self, game):
        render_frame(game, game.screen, game.font, game.hud_padding)

        if not game.state.game_over and game.state.can_show_hud:
            game.hud.update(game, game.font, game.screen, game.hud_ratio,
                            game.hud_padding)

        if game.input.cursor_visible:
            pos = game.input.cursor_pos if game.input.mode == INPUT_CONTROLLER else pygame.mouse.get_pos()
            game.screen.blit(game.cursor_sprite, (int(pos[0]), int(pos[1])))

        if game.state.game_over:
            game_lost(game, game.font, game.screen, game.screen_size)

        if game.state.can_screen_shake:
            if game.screen_shake > 0:
                game.screen_shake -= 1

            render_offset = game.ship.taken_damage() if game.screen_shake else [0, 0]
            if joysticks and game.screen_shake and game.state.can_rumble:
                controller.rumble(1, 2, BASE_RUMBLE_MS + 20)

            if not game.state.game_over:
                game.screen.blit(pygame.transform.scale(game.screen, game.screen_size),
                            render_offset)

        alpha = render_fade(game.screen, game.screen_size)
        game.crt.render(game.screen)