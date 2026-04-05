import pygame as pg

from scripts.shared import joysticks

def render_frame(game, screen, font, hud_padding):
    for i in game.stars:
        pg.draw.circle(screen, (255, 255, 255), (int(i[0]), int(i[1])),
                       i[2])

    game.celestials.draw(screen)
    if game.current_phase == "asteroids":
        game.asteroids.draw(screen)

    if game.current_phase in ("quiet", "asteroids"):
        game.aliens.draw(screen)

    if game.current_phase == "boss_fight":
        game.bosses.draw(screen)

    game.projectiles.draw(screen)
    game.upgrades.draw(screen)
    game.floating_numbers.draw(screen)
    for particle in game.particles:
        particle.draw(screen)

    img = game.base.copy()

    overlay_index = game.anim_frame_overlay % len(game.frames_flying)
    overlay_frame = game.frames_flying[overlay_index]
    img.blit(overlay_frame, (0, 0))

    if game.debugging:
        for i in game.asteroids:
            pg.draw.rect(screen, (255, 0, 0), i.hitbox, 2)

        for a in game.aliens:
            pg.draw.rect(screen, (255, 0, 0), a.rect, 2)

        for u in game.upgrades:
            pg.draw.rect(screen, (0, 255, 0), u.rect, 2)

        for p in game.projectiles:
            pg.draw.rect(screen, (0, 0, 255), p.rect, 2)

    if game.ship_alive:
        game.ship.rect.topleft = (game.ship_x, game.ship_y)
        screen.blit(img, game.ship.rect)
        if game.debugging:
            pg.draw.rect(screen, (255, 0, 0), game.ship.hitbox, 2)

    game.explosions.draw(screen)

    if game.skill_tab.active:
        cursor_pos = game.cursor_pos if joysticks else pg.mouse.get_pos()
        for skill in game.skills.skills:
            skill.is_hovered(cursor_pos)

        game.selected_skill = None
        for skill in game.skills.skills:
            if skill.is_hovered(cursor_pos):
                game.selected_skill = skill
                break

    game.stats_tab.render(game, screen, font, hud_padding)
    game.skill_tab.render(game, screen, font, hud_padding)

    screen.blit(game.credits, [hud_padding, 125])

    if game.tutorial_on:
        game.tutorial.render(screen, font, )


def render_skills_tab(game, screen, rect, game_font):
    perk_points = game_font.render(f"Perks: {game.ship.perk_points}", True,
                                   (255, 255, 255))
    screen.blit(perk_points, (rect.x + 40, rect.y + 40))

    for skill in game.skills.skills:
        x, y = skill.pos
        frame = pg.transform.scale(skill.current_frame(), (64, 64))
        skill.rect.topleft = (rect.x + x, rect.y + y)
        screen.blit(frame, skill.rect)
        screen.blit(skill.icon_image, skill.rect)


def render_stats_tab(game, screen, rect, game_font):
    stats = [
        f"Hitpoints: {int(game.ship.hitpoints)}/{int(game.ship.max_hitpoints)}",
        f"Shield: {int(game.ship.shield)}/{int(game.ship.max_shield)}",
        f"Ammo: {int(game.ship.ammo)}/{int(game.ship.base_ammo)}",
        f"Level: {int(game.ship.level)}",
        f"XP: {int(game.ship.xp)}/{int(game.ship.xp_to_next_level)}",
        f"Crit Chance: {int(game.ship.crit_chance * 100)}%",
        f"Crit Multiplier: {int(game.ship.crit_multiplier)}",
        f"Credits: {int(game.ship.credits)}"
    ]
    y_offset = 40
    for stat in stats:
        text_surface = game_font.render(stat, True, (255, 255, 255))
        screen.blit(text_surface, (rect.x + 40, rect.y + y_offset))
        y_offset += 50