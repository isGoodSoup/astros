import pygame
import pygame as pg

from scripts.shared import joysticks


def render_frame(game, screen, font, hud_padding):
    for i in game.stars:
        pg.draw.circle(screen, (255, 255, 255), (int(i[0]), int(i[1])), i[2])

    game.celestials.draw(screen)
    if game.current_phase in [game.phases[3], game.phases[5]]:
        game.asteroids.draw(screen)

    if game.current_phase in game.phases:
        game.aliens.draw(screen)

    if game.current_phase == game.phases[-1]:
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

    if game.debugging:
        for i in game.asteroids:
            pg.draw.rect(screen, (255, 0, 0), i.hitbox, 2)

        for a in game.aliens:
            pg.draw.rect(screen, (255, 0, 0), a.rect, 2)

        for u in game.upgrades:
            pg.draw.rect(screen, (0, 255, 0), u.rect, 2)

        for p in game.projectiles:
            pg.draw.rect(screen, (0, 0, 255), p.rect, 2)

        for b in game.bosses:
            pg.draw.rect(screen, (255, 0, 0), b.rect, 2)

    if game.ship_alive:
        game.ship.rect.topleft = (game.ship_x, game.ship_y)
        screen.blit(img, game.ship.rect)
        if game.debugging:
            pg.draw.rect(screen, (255, 0, 0), game.ship.hitbox, 2)

    game.explosions.draw(screen)

    if game.skill_tab.active and game.current_phase_options:
        cursor_pos = game.cursor_pos if joysticks else pg.mouse.get_pos()
        game.selected_skill = None
        for skill in game.current_phase_options:
            if skill.is_hovered(cursor_pos):
                game.selected_skill = skill
                break

    game.stats_tab.render(game, screen, font, hud_padding)
    game.skill_tab.render(game, screen, font, hud_padding)

    screen.blit(game.credits, [hud_padding, 190])

    if game.tutorial_on:
        game.tutorial.render(screen, font)

def render_skills_tab(game, screen, rect, game_font):
    title_text, perks = "End of Phase", f"Perks: {game.ship.perk_points}"
    title = game_font.render(title_text, True, (255, 255, 255))
    perk_points = game_font.render(perks, True, (255, 255, 255))
    padding, offset = 60, 20

    screen.blit(title, (rect.x + 250 + offset, rect.y + padding))
    screen.blit(perk_points, (rect.x + 300 + offset, rect.y + padding + 40))

    grid = [(250, 200), (350, 200), (450, 200)]
    for skill, pos in zip(game.current_phase_options, grid):
        skill.pos = (rect.x + pos[0] + offset, rect.y + pos[1])
        skill.rect.topleft = skill.pos
        skill.hovered = (skill == game.selected_skill)
        frame = pygame.transform.scale(skill.current_frame(), (64, 64))
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