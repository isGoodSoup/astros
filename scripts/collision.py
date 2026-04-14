import random

import pygame

import scripts.game as g

from scripts.explode import Explosion
from scripts.floaty import FloatingNumber
from scripts.impact import ImpactFrame
from scripts.particle import Particle
from scripts.constants import *
from scripts.utils import add_multiplier, formulize


def check_collision(game):
    if game.state.phase_index in ASTEROID_PHASES:
        asteroid_hit = pygame.sprite.spritecollideany(game.ship, game.sprites.asteroids, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
    else:
        asteroid_hit = None

    if game.state.current_phase in game.state.phases:
        alien_hit = pygame.sprite.spritecollideany(game.ship, game.sprites.aliens, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.hitbox))
    else:
        alien_hit = None

    if game.state.current_phase in game.state.phases:
        alien_proj = pygame.sprite.spritecollideany(game.ship, game.sprites.enemy_projectiles, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.rect))
    else:
        alien_proj = None

    if game.state.current_phase == game.state.phases[-1]:
        boss_hit = pygame.sprite.spritecollideany(game.ship, game.sprites.bosses, # type: ignore
            collided=lambda s,m: s.hitbox.colliderect(m.rect))
    else:
        boss_hit = None

    now = pygame.time.get_ticks()
    can_take_damage = now - game.ship.last_hit_time >= game.ship.hit_cooldown

    if asteroid_hit or alien_hit or alien_proj or boss_hit:
        if random.random() <= game.ship.evasion:
            if asteroid_hit:
                x, y = asteroid_hit.rect.center
                game.sprites.floating_numbers.add(FloatingNumber(
                    x, y, g.local.t('game.miss'), game.font, color=COLOR_LIGHT_YELLOW))
            elif alien_hit:
                x, y = alien_hit.rect.center
                game.sprites.floating_numbers.add(FloatingNumber(
                    x, y, g.local.t('game.miss'), game.font, color=COLOR_LIGHT_YELLOW))
            elif alien_proj:
                x, y = alien_proj.rect.center
                game.sprites.floating_numbers.add(FloatingNumber(
                    x, y, g.local.t('game.miss'), game.font, color=COLOR_LIGHT_YELLOW))
            return

        if alien_proj:
            alien_proj.kill()

        if can_take_damage:
            game.ship.last_hit_time = now
            game.ship.hit = True

            previous_combo = game.ship.combo_multiplier
            game.ship.combo_multiplier = 1.0

            if asteroid_hit:
                asteroid_hit.kill()

            if alien_hit:
                alien_hit.kill()

            game.ship.hit = True
            if previous_combo > 1.0:
                x, y = game.ship.rect.centerx, game.ship.rect.top
                game.sprites.floating_numbers.add(FloatingNumber(x, y, g.local.t('game.lost_mult'),
                        game.font, color=COLOR_RED))  # type: ignore

            game.sprites.explosions.add(Explosion(*game.ship.rect.center,
                                  game.sprites.frame_explode))  # type: ignore

            for _ in range(PARTICLES_AMOUNT):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.sprites.particles.append(Particle(game.ship.rect.center, vel))

            if game.state.play_sound:
                game.mixer.play(1)

            damage_per_frame = 0
            boss_damage = BOSS_DAMAGE if boss_hit else 0
            damage_taken = game.ship.damage_taken_multiplier
            if not TOGGLE_INVINCIBLE:
                if game.ship.shield > 0:
                    damage_per_frame = max(1,game.ship.max_shield // SHIP_SHIELD_FRAMES) * game.ship.level * damage_taken
                    game.ship.shield -= damage_per_frame + boss_damage
                else:
                    damage_per_frame = max(1,game.ship.max_hitpoints // SHIP_HITPOINTS_FRAMES) * game.ship.level * damage_taken
                    game.ship.hitpoints -= damage_per_frame + boss_damage

            if hasattr(game.ship, "fortified_percent"):
                if game.ship.fortified_percent > 0:
                    shield_gain = int(damage_per_frame * game.ship.fortified_percent)
                    if hasattr(game.ship, "fortified_cap"):
                        shield_gain = min(shield_gain, game.ship.fortified_cap)
                    game.ship.shield += shield_gain
            
            if game.state.can_screen_shake:
                game.screen_shake = SCREEN_SHAKE // 2

            if game.ship.hitpoints <= 0:
                game.state.game_over = True
                game.ship.kill()
                game.sprites.ship_alive = False
                pygame.mixer.music.stop()
                game.state.game_over = True

    hits1 = pygame.sprite.groupcollide(game.sprites.projectiles, game.sprites.asteroids, True,
                                   False)
    for projectile, asteroids_hit in hits1.items():
        for asteroid in asteroids_hit:
            current_time = pygame.time.get_ticks()
            if current_time > game.ship.maniac_boost_end:
                game.ship.maniac_boost = 0

            effective_crit_chance = min(1.0, game.ship.crit_chance + game.ship.maniac_boost)
            if random.random() < effective_crit_chance:
                damage_per_frame = game.ship.damage * game.ship.crit_multiplier
                color = COLOR_LIGHT_RED
                size = SHIP_CRIT_CHANCE_SIZE
            else:
                damage_per_frame = game.ship.damage
                color = COLOR_LIGHT_ORANGE
                size = SHIP_DAMAGE_SIZE

            if not game.ship.hit:
                game.ship.combo_multiplier += SHIP_COMBO_ADDITION if not game.ship.is_commando_active \
                    else SHIP_NERFED_COMBO_ADDITION
            total_multiplier = game.ship.combo_multiplier * game.ship.powerup_multiplier
            damage_per_frame *= total_multiplier

            if game.ship.hit:
                game.ship.combo_multiplier = 1.0

            asteroid.hitpoints -= damage_per_frame
            x, y = asteroid.rect.center

            if not game.ship.hit:
                mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
                add_multiplier(game, mult_x, mult_y,
                               f"x{total_multiplier:.2f}",
                               color=color, font_size=size)

            game.sprites.floating_numbers.add(FloatingNumber(x, y, int(damage_per_frame), game.font, color=color,
                               font_size=size))
            impact = ImpactFrame(asteroid.rect.centerx, asteroid.rect.centery,
                                 game.sprites.frame_explode[0])
            game.sprites.explosions.add(impact)
            for _ in range(PARTICLES_AMOUNT):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.sprites.particles.append(Particle((asteroid.rect.centerx,
                                                asteroid.rect.centery), vel))

            if asteroid.hitpoints <= 0:
                asteroid.kill()
                game.ship.credits += (random.randint(1, SHIP_CREDITS_CAP) *
                                      game.ship.credits_multiplier)
                if maniac_skill := next(
                        (s for s in game.skills.get_unlocked() if
                         s.name == "Maniac"), None):
                    maniac_skill.ability.apply(game.ship, maniac_skill.level)
                explosion = Explosion(asteroid.rect.centerx,
                                      asteroid.rect.centery, game.sprites.frame_explode)
                game.sprites.explosions.add(explosion)
                if game.state.play_sound:
                    game.mixer.play(1)
                game.state.score_multiplier = game.ship.combo_multiplier
                game.state.score += (game.ship.level * SCORE_SCALING *
                                game.state.score_multiplier)
                game.ship.gain_xp(formulize(game, game.ship.level), game.mixer.sounds)

    hits2 = pygame.sprite.groupcollide(game.sprites.projectiles, game.sprites.aliens, True, False)
    for projectile, aliens_hit in hits2.items():
        for alien in aliens_hit:
            current_time = pygame.time.get_ticks()
            if current_time > game.ship.maniac_boost_end:
                game.ship.maniac_boost = 0

            effective_crit_chance = min(1.0, game.ship.crit_chance + game.ship.maniac_boost)
            if random.random() < effective_crit_chance:
                damage_per_frame = game.ship.damage * game.ship.crit_multiplier
                color = COLOR_LIGHT_RED
                size = SHIP_CRIT_CHANCE_SIZE
            else:
                damage_per_frame = game.ship.damage
                color = COLOR_LIGHT_ORANGE
                size = SHIP_DAMAGE_SIZE

            if not game.ship.hit:
                game.ship.combo_multiplier += SHIP_COMBO_ADDITION if not game.ship.is_commando_active \
                    else SHIP_NERFED_COMBO_ADDITION
            total_multiplier = game.ship.combo_multiplier * game.ship.powerup_multiplier
            damage_per_frame *= total_multiplier

            if game.ship.hit:
                game.ship.combo_multiplier = 1.0

            alien.hitpoints -= damage_per_frame
            x, y = alien.rect.center

            if not game.ship.hit:
                mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
                add_multiplier(game, mult_x, mult_y,
                               f"x{total_multiplier:.2f}",
                               color=color, font_size=size)

            game.sprites.floating_numbers.add(FloatingNumber(x, y, int(damage_per_frame), game.font, color=color,
                               font_size=size))
            impact = ImpactFrame(alien.rect.centerx, alien.rect.centery,
                                 game.sprites.frame_explode[0])
            game.sprites.explosions.add(impact)
            for _ in range(PARTICLES_AMOUNT):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.sprites.particles.append(Particle((alien.rect.centerx, alien.rect.centery), vel))

            if alien.hitpoints <= 0:
                alien.kill()
                game.ship.credits += random.randint(1, SHIP_CREDITS_CAP) * game.ship.credits_multiplier
                if maniac_skill := next(
                        (s for s in game.skills.get_unlocked() if
                         s.name == "Maniac"), None):
                    maniac_skill.ability.apply(game.ship, maniac_skill.level)
                explosion = Explosion(alien.rect.centerx, alien.rect.centery,
                                      game.sprites.frame_explode)
                game.sprites.explosions.add(explosion)
                if game.state.play_sound:
                    game.mixer.play(1)
                game.state.score_multiplier = game.ship.combo_multiplier
                game.state.score += (game.ship.level * SCORE_SCALING * game.state.score_multiplier)
                game.ship.gain_xp(formulize(game, game.ship.level), game.mixer.sounds)

    hits3 = pygame.sprite.groupcollide(game.sprites.projectiles, game.sprites.bosses, True, False)
    for projectile, boss_hit in hits3.items():
        for boss in boss_hit:
            current_time = pygame.time.get_ticks()
            if current_time > game.ship.maniac_boost_end:
                game.ship.maniac_boost = 0

            effective_crit_chance = min(1.0, game.ship.crit_chance + game.ship.maniac_boost)
            if random.random() < effective_crit_chance:
                damage_per_frame = game.ship.damage * game.ship.crit_multiplier
                color = COLOR_LIGHT_RED
                size = SHIP_CRIT_CHANCE_SIZE
            else:
                damage_per_frame = game.ship.damage
                color = COLOR_LIGHT_ORANGE
                size = SHIP_DAMAGE_SIZE

            if not game.ship.hit:
                game.ship.combo_multiplier += SHIP_COMBO_ADDITION if not game.ship.is_commando_active \
                    else SHIP_NERFED_COMBO_ADDITION
            total_multiplier = game.ship.combo_multiplier * game.ship.powerup_multiplier
            damage_per_frame *= total_multiplier

            if game.ship.hit:
                game.ship.combo_multiplier = 1.0

            boss.hitpoints -= damage_per_frame
            x, y = boss.rect.center

            if not game.ship.hit:
                mult_x, mult_y = game.ship.rect.centerx, game.ship.rect.top
                add_multiplier(game, mult_x, mult_y,
                               f"x{total_multiplier:.2f}",
                               color=color, font_size=size)

            game.sprites.floating_numbers.add(FloatingNumber(x, y, int(damage_per_frame), game.font, color=color,
                               font_size=size))
            impact = ImpactFrame(boss.rect.centerx, boss.rect.centery,
                                 game.sprites.frame_explode[0])
            game.sprites.explosions.add(impact)
            for _ in range(PARTICLES_AMOUNT):
                vel = [random.uniform(-2, 2), random.uniform(-2, 2)]
                game.sprites.particles.append(
                    Particle((boss.rect.centerx, boss.rect.centery), vel))

            if boss.hitpoints <= 0:
                boss.kill()
                game.ship.credits += random.randint(1, SHIP_CREDITS_CAP) * game.ship.credits_multiplier
                if maniac_skill := next(
                        (s for s in game.skills.get_unlocked() if
                         s.name == "Maniac"), None):
                    maniac_skill.ability.apply(game.ship, maniac_skill.level)
                explosion = Explosion(boss.rect.centerx, boss.rect.centery,
                                      game.sprites.frame_explode)
                game.sprites.explosions.add(explosion)
                if game.state.play_sound:
                    game.mixer.play(1)
                game.state.score_multiplier = game.ship.combo_multiplier
                game.state.score += game.ship.level * SCORE_SCALING * game.state.score_multiplier
                game.ship.gain_xp(formulize(game, game.ship.level), game.mixer.sounds)

    for projectile in list(game.sprites.projectiles):
        if getattr(projectile, "nuke", False):
            game.events.nuke_event(projectile.rect.center, game)
            projectile.kill()

    upgrade_hit = pygame.sprite.spritecollide(game.ship, game.sprites.upgrades,False, # type: ignore
                                          collided=lambda s,u: s.hitbox.colliderect(u.rect))
    if upgrade_hit:
        for upgrade in upgrade_hit:
            upgrade.kill()
            if game.state.play_sound:
                game.mixer.play(2)
                upgrade.apply(game.ship, game)