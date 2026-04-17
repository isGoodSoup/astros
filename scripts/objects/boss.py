import math
import random

import pygame

from scripts.engine.shared import joysticks, controller
from scripts.engine.utils import resource_path, HealthBar, colour, update_screenshake
from scripts.objects.proj import Projectile, StoneProjectile
from scripts.objects.shockwave import Shockwave
from scripts.system.constants import *
from scripts.system.levels import DIFFICULTY_ENEMY_SETTINGS


class Boss(pygame.sprite.Sprite):
    def __init__(self, game, ship, projectiles, x, y, color, frame=0,
                 width=ALIEN_WIDTH, height=ALIEN_HEIGHT, scale=SCALE * 2,
                 columns=1, offset_x=0, offset_y=0):
        super().__init__()
        self.color = color
        self.image = pygame.image.load(
            resource_path(f"assets/aliens/{color}.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image,
                                            (width * scale, height * scale))
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(self.rect.width * -0.5, self.rect.height * -0.5)

        self.pos = pygame.Vector2(x, y)
        self.game = game
        self.ship = ship
        settings = DIFFICULTY_ENEMY_SETTINGS[self.game.state.difficulty]
        self.step = max(1, int((ship.velocity + 1) * settings["speed_multiplier"]))
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.direction = 1
        self.shooting = False
        self.moving = False

        self.colors = BOSS_COLORS
        self.level = ship.level + BOSS_ADVANTAGE
        self.max_hitpoints = int(
            (BOSS_BASE_HITPOINTS * self.level + self.colors.get(color))
            * settings["hp_multiplier"])
        self.hitpoints = self.max_hitpoints
        self.base_damage = int(
            (ship.damage * self.level) * settings["damage_multiplier"])
        self.current_damage = self.base_damage
        self.last_shot_time = 0
        self.shot_cooldown = int(
            HIGH_FIRE_RATE / settings["fire_rate_multiplier"])
        self.last_move = pygame.time.get_ticks()
        self.move_timer = pygame.time.get_ticks()
        self.hit = False
        self.boss_phases = BOSS_PHASES
        self.current_phase = self.boss_phases[0]
        self.phase_index = 0

        self.velocity = pygame.Vector2(
            random.choice([-1, 1]) * random.uniform(3, 6),
            random.choice([-1, 1]) * random.uniform(3, 6)
        )
        self.phase2_change_time = pygame.time.get_ticks()
        self.phase2_change_interval = ONE_SECOND

        self.orbit_radius = random.randint(300, 500)
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.orbit_speed = random.uniform(0.1, 0.4)

        self.projectiles = projectiles

        self.target = pygame.Vector2(
            self.ship.rect.midbottom[0] + self.offset_x,
            self.offset_y
        )

        self.last_summon_time = 0
        self.summon_cooldown = EVOKER_SUMMON_COOLDOWN * 2
        self.exploded = False

        self.health_bar = HealthBar(self, width=HEALTHBAR_WIDTH * 4, offset=20)
        self.health_bar.visible = True

        self.original_image = self.image
        self.hit_flash_timer = 0
        self.hit_flash_duration = 8

        self.iframes_cooldown = BOSS_IFRAMES
        self.iframes_duration = BOSS_IFRAMES_DURATION
        self.is_invincible = False
        self.iframes_timer = pygame.time.get_ticks()
        self.iframes_start_time = 0
        self.original_step = self.step
        self.original_velocity = self.velocity.copy()
        self.alpha_direction = 1
        self.alpha = 255

    def update(self):
        self.update_hit_flash()
        self.health_bar.update()
        self.hitbox.center = self.rect.center
        now = pygame.time.get_ticks()

        if not self.is_invincible:
            if now - self.iframes_timer >= self.iframes_cooldown:
                self.is_invincible = True
                self.iframes_start_time = now
                self.original_step = self.step
                self.original_velocity = self.velocity.copy()
        else:
            elapsed = now - self.iframes_start_time
            if elapsed >= self.iframes_duration:
                self.is_invincible = False
                self.iframes_timer = now
                self.step = self.original_step
                self.velocity = self.original_velocity.copy()
                self.current_damage = self.base_damage
                self.alpha = 255
                self.image.set_alpha(self.alpha)
            else:
                seconds_passed = elapsed // 1000
                multiplier = 1.0 + (0.02 * seconds_passed)
                self.step = self.original_step * multiplier
                if self.velocity.length() > 0:
                    self.velocity = self.original_velocity * multiplier
                self.current_damage = self.base_damage * multiplier

                self.alpha += 5 * self.alpha_direction
                if self.alpha >= 255:
                    self.alpha = 255
                    self.alpha_direction = -1
                elif self.alpha <= 180:
                    self.alpha = 180
                    self.alpha_direction = 1
                self.image.set_alpha(self.alpha)

        if self.current_phase in ['phase1', 'phase2', 'phase3']:
            phase_multipliers = {
                'phase1': (0.02, 1.0, 1.5),
                'phase2': (0.03, 0.8, 2.0),
                'phase3': (0.04, 0.5, 2.5)
            }
            angle_inc, radius_mult, speed_mult = phase_multipliers[self.current_phase]

            self.orbit_angle += self.orbit_speed * angle_inc

            target_pos = pygame.Vector2(
                self.ship.rect.centerx + math.cos(
                    self.orbit_angle) * (self.orbit_radius * radius_mult),
                self.ship.rect.centery + math.sin(
                    self.orbit_angle) * (self.orbit_radius * radius_mult)
            )

            pos = pygame.Vector2(self.rect.center)
            direction = (target_pos - pos)

            if direction.length() > 2:
                lerp_factor = min(1.0, (self.step * speed_mult) / direction.length())
                new_pos = pos.lerp(target_pos, lerp_factor)
                self.rect.center = (int(new_pos.x), int(new_pos.y))

            if now - self.last_shot_time >= self.shot_cooldown:
                self.last_shot_time = now
                self.shoot()

            if self.color == "purple":
                if now - self.last_summon_time > self.summon_cooldown:
                    self.summon()
                    self.last_summon_time = now

        health_ratio = self.hitpoints / self.max_hitpoints
        if health_ratio < 0.7 and self.current_phase == 'phase1':
            self.current_phase = 'phase2'
        elif health_ratio < 0.5 and self.current_phase == 'phase2':
            self.current_phase = 'phase3'

    def update_hit_flash(self):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
            if self.hit_flash_timer > self.hit_flash_duration - 2:
                self.image = colour(self.original_image, COLOR_WHITE)
            elif (self.hit_flash_timer // 2) % 2 == 0:
                self.image = colour(self.original_image, COLOR_WHITE)
            else:
                self.image = self.original_image
        else:
            self.image = self.original_image

    def trigger_hit_flash(self):
        self.hit_flash_timer = self.hit_flash_duration

    def shoot(self):
        settings = DIFFICULTY_ENEMY_SETTINGS[self.game.state.difficulty]
        if self.color == "green":
            self.shoot_boomerang()
            return

        target_vec = pygame.Vector2(self.ship.rect.center) - pygame.Vector2(
            self.rect.center)
        if target_vec.length() != 0:
            direction = target_vec.normalize()
        else:
            direction = pygame.Vector2(0, 1)

        angle_offset = random.uniform(-0.2, 0.2)

        direction.rotate_ip(math.degrees(angle_offset))
        self.projectiles.add(Projectile(
            self.rect.center, COLOR_RED,
            direction=(direction.x, direction.y),
            speed=16, damage=int(self.current_damage),
            range_limit=ONE_SECOND))

    def shoot_boomerang(self):
        target = pygame.Vector2(self.ship.rect.center)
        pos = pygame.Vector2(self.rect.center)
        direction = (target - pos)
        if direction.length() > 0:
            direction = direction.normalize()
            settings = DIFFICULTY_ENEMY_SETTINGS[self.game.state.difficulty]
            stone = StoneProjectile(
                self.rect.center, direction, self.game,
                damage=int(self.current_damage),
                parent=self)
            self.game.sprites.enemy_projectiles.add(stone)

    def summon(self):
        from scripts.objects.particle import Particle
        from scripts.objects.enemies import Alien
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.game.sprites.particles.append(
                Particle(self.rect.center, velocity, timer=30, color=COLOR_RED)
            )

        for _ in range(random.randint(1, 2)):
            off_x = random.randint(-100, 100)
            off_y = random.randint(-100, 100)
            new_alien = Alien("red", self.rect.centerx + off_x,
                              self.rect.centery + off_y, self.ship, self.game)
            new_alien.aggro = True
            new_alien.in_formation = False
            self.game.sprites.aliens.add(new_alien)

    def explode(self):
        if not self.exploded:
            self.exploded = True
            self.game.sprites.shockwaves.append(Shockwave(self.rect.center,
                                                          max_radius=400))
            if self.game.state.screen_shake_amount > 0:
                update_screenshake(game, time=40,
                                   strength=game.state.screen_shake_amount * 8)

            if joysticks and self.game.state.can_rumble:
                controller.rumble(0.5, 0.7, BASE_RUMBLE_MS * 4)

            dist = pygame.Vector2(self.rect.center).distance_to(
                self.ship.rect.center)
            if dist < 400:
                damage_taken = self.ship.damage_taken_multiplier
                total_damage = self.base_damage * 2 * damage_taken
                if self.ship.shield > 0:
                    self.ship.shield -= total_damage
                else:
                    self.ship.hitpoints -= total_damage
                self.ship.hit = True
                self.ship.last_hit_time = pygame.time.get_ticks()

    def kill(self):
        if self.color == "orange":
            self.explode()
        super().kill()
