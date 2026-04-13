import pygame

import scripts.assets as assets
from scripts.lang import local
from scripts.runtime import get_desc
from scripts.settings import (TOGGLE_TUTORIAL, COLOR_BLUE, COLOR_RED, \
                              COLOR_GREEN, COLOR_WHITE, STAT_Y_OFFSET,
                              SKILL_TAB_OFFSETS, ASTEROID_PHASES,
                              INPUT_CONTROLLER, SCALE, PAUSED_TEXT_Y,
                              SKILL_TAB_PADDING, SKTAB_HEADER_OFFSET,
                              SKILL_TAB_GRID, ALPHA)
from scripts.shared import joysticks
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
        pause_text = local.t('game.pause')
        pause = game.font.render(pause_text, True, COLOR_WHITE)
        surf = assets.OVERLAY_CONTROLLER if (game.input.mode ==
            INPUT_CONTROLLER) else assets.OVERLAY_KEYBOARD

        surf = pygame.transform.scale(surf, (surf.get_width() * SCALE,
                                             surf.get_height() * SCALE))

        dim_surface = pygame.Surface(game.screen_size)
        dim_surface.fill((0, 0, 0))
        dim_surface.set_alpha(ALPHA)

        if not game.hud.skill_tab.active and not game.hud.settings_tab.active:
            screen.blit(dim_surface, (0, 0))
            screen.blit(surf, [game.screen_size[0]//2 - surf.get_width()//2,
                               game.screen_size[1]//2 - surf.get_height()//2])
            screen.blit(pause, [game.screen_size[0]//2 - pause.get_width()//2, PAUSED_TEXT_Y])

        game.hud.settings_tab.render(game, screen, font, hud_padding)

def render_skills_tab(game, screen, rect, game_font):
    title_text, perks = local.t('game.victory'), local.t("game.hud.perks",
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

            text = local.t(skill.description_key)
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
        local.t("game.hud.hitpoints", hp=int(game.ship.hitpoints),
                max_hp=int(game.ship.max_hitpoints)),
        local.t("game.hud.shield", shield=int(game.ship.shield),
                max_shield=int(game.ship.max_shield)),
        local.t("game.hud.ammo", ammo=int(available_ammo),
                max_ammo=int(game.ship.arsenal)),
        local.t("game.hud.level", level=int(game.ship.level)),
        local.t("game.hud.xp", xp=int(game.ship.xp),
                xp_to_next_level=int(game.ship.xp_to_next_level)),
        local.t("game.hud.crit_chance",
                crit_chance=int(game.ship.crit_chance * 100)),
        local.t("game.hud.crit_multiplier",
                crit_multiplier=int(game.ship.crit_multiplier)),
    ]

    y_offset = STAT_Y_OFFSET
    for stat in stats:
        text_surface = game_font.render(stat, True, COLOR_WHITE)
        screen.blit(text_surface, (rect.x + 40, rect.y + y_offset))
        y_offset += 50

def render_settings_tab(game, screen, rect, game_font):
    header_settings = local.t('game.settings.header')
    surf = game_font.render(header_settings, True, COLOR_WHITE)
    screen.blit(surf, [rect.x + SKTAB_HEADER_OFFSET + 50, rect.y + 100])

    bar_x = rect.x + 100
    bar_y = rect.y + 140
    bar_width = 200
    bar_height = 20

    volume = game.volume
    fill_width = int(bar_width * volume)
    pygame.draw.rect(screen, (60, 60, 60),
                     (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, COLOR_WHITE,
                     (bar_x, bar_y, fill_width, bar_height))

def render_waves(game, screen):
    for wave in game.sprites.shockwaves:
        alpha = max(0, 255 * (1 - wave.radius / wave.max_radius))
        surf = pygame.Surface((wave.radius * 2, wave.radius * 2),
                              pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, int(alpha)),
            (wave.radius, wave.radius), int(wave.radius), 6)

        screen.blit(surf,
            (wave.x - wave.radius, wave.y - wave.radius))