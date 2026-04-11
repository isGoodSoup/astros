import pygame

from scripts.settings import (TOGGLE_TUTORIAL, COLOR_BLUE, COLOR_RED, \
                              COLOR_GREEN, COLOR_WHITE, STAT_Y_OFFSET,
                              SKILL_TAB_OFFSETS, ASTEROID_PHASES)
from scripts.shared import joysticks
from scripts.utils import wrap_text


def render_frame(game, screen, font, hud_padding):
    now = pygame.time.get_ticks()

    boss_invisible = (
            hasattr(game, "boss_invisible_start") and
            now - game.boss_invisible_start < game.boss_invisible_duration
    )

    for i in game.stars:
        pygame.draw.circle(screen, COLOR_WHITE, (int(i[0]), int(i[1])), i[2])

    game.celestials.draw(screen)
    if game.state.phase_index in ASTEROID_PHASES:
        game.asteroids.draw(screen)

    if len(game.aliens) > 0:
        game.aliens.draw(screen)

    if not boss_invisible:
        game.bosses.draw(screen)

    game.projectiles.draw(screen)
    game.enemy_projectiles.draw(screen)
    game.upgrades.draw(screen)
    game.floating_numbers.draw(screen)

    for particle in game.particles:
        particle.draw(screen)

    img = game.base.copy()

    overlay_index = game.anim_frame_overlay % len(game.frames_flying)
    overlay_frame = game.frames_flying[overlay_index]
    img.blit(overlay_frame, (0, 0))

    if game.state.debugging:
        for i in game.asteroids:
            pygame.draw.rect(screen, COLOR_RED, i.hitbox, 2)

        for a in game.aliens:
            pygame.draw.rect(screen, COLOR_RED, a.rect, 2)

        for u in game.upgrades:
            pygame.draw.rect(screen, COLOR_GREEN, u.rect, 2)

        for p in game.projectiles:
            pygame.draw.rect(screen, COLOR_BLUE, p.rect, 2)

        for b in game.bosses:
            pygame.draw.rect(screen, COLOR_RED, b.rect, 2)

    if game.ship_alive:
        game.ship.rect.topleft = (game.ship.rect.x, game.ship.rect.y)
        screen.blit(img, game.ship.rect)
        if game.state.debugging:
            pygame.draw.rect(screen, COLOR_RED, game.ship.hitbox, 2)

    game.explosions.draw(screen)

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

    render_waves(game)

    game.hud.stats_tab.render(game, screen, font, hud_padding)
    game.hud.skill_tab.render(game, screen, font, hud_padding)

    if TOGGLE_TUTORIAL:
        game.tutorial.render(screen, font)

    if game.state.pause and (not game.hud.skill_tab.active or not
            game.hud.stats_tab.active):
        pause_text = "PAUSED"
        pause = game.font.render(pause_text, True, COLOR_WHITE)
        if not game.hud.skill_tab.active:
            screen.blit(pause, [game.screen_size[0]//2 - pause.get_width()//2,
                        game.screen_size[1]//2 - pause.get_height()//2])

def render_skills_tab(game, screen, rect, game_font):
    title_text, perks = "Victory!", f"Perks: {game.ship.perk_points}"
    title = game_font.render(title_text, True, COLOR_WHITE)
    perk_points = game_font.render(perks, True, COLOR_WHITE)
    padding, offset = SKILL_TAB_OFFSETS

    screen.blit(title, (rect.x + 300 + offset, rect.y + padding))
    screen.blit(perk_points, (rect.x + 300 + offset, rect.y + padding + 40))

    cursor_pos = game.input.cursor_pos if game.input.mode == "controller" \
        else pygame.mouse.get_pos()
    grid = [(250, 200), (350, 200), (450, 200)]
    for i, (skill, pos) in enumerate(zip(game.state.current_phase_options, grid)):
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
            desc_rect = pygame.Rect(rect.x + 50, rect.y + 300, rect.width - 100, 150)
            description_surface = game_font.render(skill.description, True,
                                                   COLOR_WHITE)
            description_rect = description_surface.get_rect(center=desc_rect.center)

            lines = wrap_text(skill.description, game_font.get_font(),
                              desc_rect.width)
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
        f"Hitpoints: {int(game.ship.hitpoints)}/{int(game.ship.max_hitpoints)}",
        f"Shield: {int(game.ship.shield)}/{int(game.ship.max_shield)}",
        f"Ammo: {int(available_ammo)}/{int(game.ship.arsenal)}",
        f"Level: {int(game.ship.level)}",
        f"XP: {int(game.ship.xp)}/{int(game.ship.xp_to_next_level)}",
        f"Crit Chance: {int(game.ship.crit_chance * 100)}%",
        f"Crit Multiplier: {int(game.ship.crit_multiplier)}",
    ]

    y_offset = STAT_Y_OFFSET
    for stat in stats:
        text_surface = game_font.render(stat, True, COLOR_WHITE)
        screen.blit(text_surface, (rect.x + 40, rect.y + y_offset))
        y_offset += 50

def render_waves(game):
    for wave in game.shockwaves:
        alpha = max(0, 255 * (1 - wave.radius / wave.max_radius))
        surf = pygame.Surface((wave.radius * 2, wave.radius * 2),
                              pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 255, int(alpha)),
            (wave.radius, wave.radius), int(wave.radius), 6)

        game.screen.blit(surf,
            (wave.x - wave.radius, wave.y - wave.radius))