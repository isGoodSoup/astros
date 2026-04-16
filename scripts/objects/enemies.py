import random
import math
import pygame

from scripts.objects.entity import Entity
from scripts.system.levels import (DIFFICULTY_ENEMY_SETTINGS)
from scripts.objects.shockwave import Shockwave
from scripts.objects.proj import Projectile, StoneProjectile
from scripts.engine.shared import joysticks, controller
from scripts.system.constants import *
from scripts.engine.utils import resource_path, HealthBar

__all__ = ['Alien', 'HeavyAlien', 'BomberAlien', 'EvokerAlien',
           'StoneAlien', 'AlienBehemoth', 'AlienMinion']


class Alien(Entity):
    def __init__(self, color, x, y, ship, game,
                 base_hp=100, base_damage=10, base_speed=4, base_weight=1):
        image_path = resource_path(f"assets/aliens/{color}.png")
        image = pygame.image.load(image_path).convert_alpha()
        super().__init__(image, x, y)
        self.ship = ship
        self.game = game
        self.color = color
        self.base_hp = base_hp
        self.base_damage = base_damage
        self.base_speed = base_speed
        self.is_elite = self._roll_elite()

        self.formation_offset = (0, 0)
        self.formation_center = pygame.Vector2(x, y)
        self.in_formation = True
        self.aggro = False
        self.aggro_distance = 400

        self.orbit_radius = random.randint(150, 300)
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.orbit_speed = random.uniform(0.5, 1.5)

        self.last_shot_time = 0

        self.health_bar = HealthBar(self)

        self._apply_difficulty()

    def _get_scalers(self):
        return DIFFICULTY_ENEMY_SETTINGS[self.game.state.difficulty]

    def _apply_difficulty(self):
        settings = self._get_scalers()

        hp = self.base_hp * settings["hp_multiplier"]
        dmg = self.base_damage * settings["damage_multiplier"]
        spd = self.base_speed * settings["speed_multiplier"]

        fire_rate = settings["fire_rate_multiplier"]

        if self.is_elite:
            hp *= 2.0
            dmg *= 2.0
            spd *= 1.25
            fire_rate *= 1.5

        self.hitpoints = int(hp)
        self.damage = int(dmg)
        self.speed = spd

        self.fire_rate_multiplier = fire_rate
        self.elite_chance = settings["elite_chance"]

        self.last_shot_time = 0
        self.shot_cooldown = 1000

    def _roll_elite(self):
        settings = self._get_scalers()
        return random.random() < settings["elite_chance"]

    def force_elite(self):
        self.is_elite = True
        self._apply_difficulty()

    def refresh_difficulty(self):
        self._apply_difficulty()

    def update(self):
        self.health_bar.update()
        if not self.aggro:
            dist_to_ship = pygame.Vector2(self.rect.center).distance_to(
                self.ship.rect.center)
            if int(dist_to_ship) < self.aggro_distance:
                self.aggro = True
                self.in_formation = False

        if self.in_formation:
            if (not hasattr(self.game,
                           "_last_formation_update") or
                    self.game._last_formation_update != pygame.time.get_ticks()):
                self.formation_center.y += self.speed
                self.game._last_formation_update = pygame.time.get_ticks()

            self.rect.center = self.formation_center + self.formation_offset

            if self.rect.top > self.game.screen_size[1] + 100:
                self.kill()
        else:
            self.orbit_angle += self.orbit_speed * 0.02

            target_pos = pygame.Vector2(
                self.ship.rect.centerx + math.cos(
                    self.orbit_angle) * self.orbit_radius,
                self.ship.rect.centery + math.sin(
                    self.orbit_angle) * self.orbit_radius
            )

            pos = pygame.Vector2(self.rect.center)
            direction = (target_pos - pos)

            if direction.length() > 5:
                direction = direction.normalize()
                pos += direction * self.speed * 1.5
                self.rect.center = pos

            margin = 50
            if self.rect.left < -margin: self.rect.left = -margin
            if self.rect.right > self.game.screen_size[
                0] + margin: self.rect.right = self.game.screen_size[0] + margin
            if self.rect.top < -margin: self.rect.top = -margin
            if self.rect.bottom > self.game.screen_size[1] + margin:
                self.rect.bottom = self.game.screen_size[1] + margin

    def shoot(self, target, cooldown):
        if not self.aggro or not self.alive():
            return None

        now = pygame.time.get_ticks()
        actual_cooldown = cooldown / self.fire_rate_multiplier

        if now - self.last_shot_time > actual_cooldown:
            self.last_shot_time = now

            pos = pygame.Vector2(self.rect.center)
            target_pos = pygame.Vector2(target.rect.center)
            direction = (target_pos - pos)

            if direction.length() > 0:
                direction = direction.normalize()
                projectile = Projectile(
                    pos,
                    COLOR_LIGHT_RED,
                    direction=direction,
                    speed=8,
                    damage=self.damage
                )
                return [projectile]
        return None


class HeavyAlien(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("yellow", x, y, ship, game, base_hp=200,
                         base_damage=20)


class BomberAlien(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("orange", x, y, ship, game, base_damage=20)
        self.exploded = False
        self.aggro_distance = 500

    def update(self):
        self.health_bar.update()
        if not self.aggro:
            dist_to_ship = pygame.Vector2(self.rect.center).distance_to(
                self.ship.rect.center)
            if int(dist_to_ship) < self.aggro_distance:
                self.aggro = True
                self.in_formation = False

        if self.in_formation:
            if (not hasattr(self.game,
                           "_last_formation_update") or
                    self.game._last_formation_update != pygame.time.get_ticks()):
                self.formation_center.y += self.speed
                self.game._last_formation_update = pygame.time.get_ticks()

            self.rect.center = self.formation_center + self.formation_offset

            if self.rect.top > self.game.screen_size[1] + 100:
                self.kill()
        else:
            target = pygame.Vector2(self.ship.rect.center)
            pos = pygame.Vector2(self.rect.center)
            direction = (target - pos)
            if direction.length() > 0:
                direction = direction.normalize()
                pos += direction * self.speed * 2.0
                self.rect.center = pos

            if self.aggro and not self.exploded:
                dist = pygame.Vector2(self.rect.center).distance_to(
                    self.ship.rect.center)
                if dist < 50:
                    self.explode()

            if self.rect.top > self.game.screen_size[1]:
                self.rect.bottom = 0

    def explode(self):
        if not self.exploded:
            self.exploded = True
            self.game.sprites.shockwaves.append(Shockwave(self.rect.center,
                                                          max_radius=200))

            if self.game.state.can_screen_shake:
                self.game.screen_shake = SCREEN_SHAKE
            if joysticks and self.game.state.can_rumble:
                controller.rumble(0.2, 0.4, BASE_RUMBLE_MS * 2)

            dist = pygame.Vector2(self.rect.center).distance_to(
                self.ship.rect.center)
            if dist < 200:
                damage_taken = self.ship.damage_taken_multiplier
                total_damage = self.damage * 2 * damage_taken
                if self.ship.shield > 0:
                    self.ship.shield -= total_damage
                else:
                    self.ship.hitpoints -= total_damage
                self.ship.hit = True
                self.ship.last_hit_time = pygame.time.get_ticks()

            self.kill()

    def kill(self):
        if not self.exploded:
            self.explode()
        else:
            super().kill()

class EvokerAlien(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("purple", x, y, ship, game, base_hp=500,
                         base_damage=30)
        self.summon_cooldown = EVOKER_SUMMON_COOLDOWN
        self.last_summon_time = pygame.time.get_ticks()

    def update(self):
        super().update()
        now = pygame.time.get_ticks()
        if self.aggro and now - self.last_summon_time > self.summon_cooldown:
            self.summon()
            self.last_summon_time = now

    def summon(self):
        from scripts.objects.particle import Particle
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.game.sprites.particles.append(
                Particle(self.rect.center, velocity, timer=30, color=COLOR_WHITE)
            )

        for _ in range(random.randint(2, 3)):
            off_x = random.randint(-100, 100)
            off_y = random.randint(-100, 100)
            new_alien = Alien("red", self.rect.centerx + off_x,
                              self.rect.centery + off_y, self.ship, self.game)
            new_alien.aggro = True
            new_alien.in_formation = False
            self.game.sprites.aliens.add(new_alien)

class StoneAlien(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("green", x, y, ship, game, base_hp=250,
                         base_damage=20)
        self.shot_cooldown = 3000

    def update(self):
        super().update()
        now = pygame.time.get_ticks()
        if self.aggro and now - self.last_shot_time > self.shot_cooldown:
            self.shoot_boomerang()
            self.last_shot_time = now

    def shoot_boomerang(self):
        target = pygame.Vector2(self.ship.rect.center)
        pos = pygame.Vector2(self.rect.center)
        direction = (target - pos)
        if direction.length() > 0:
            direction = direction.normalize()
            stone = StoneProjectile(self.rect.center, direction, self.game,
                                    damage=self.damage, parent=self)
            self.game.sprites.enemy_projectiles.add(stone)

class AlienBehemoth(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("blue", x, y, ship, game, base_hp=2000, base_damage=50)
        self.shot_cooldown = 5000
        self.aggro_distance = 500
        
        self.scale_factor = random.uniform(2.0, 3.0)
        self.image = pygame.transform.scale(
            self.image, 
            (int(self.rect.width * self.scale_factor), 
             int(self.rect.height * self.scale_factor))
        )
        self.rect = self.image.get_rect(center=self.rect.center)
        
        self.summon_cooldown = EVOKER_SUMMON_COOLDOWN * 1.5
        self.last_summon_time = pygame.time.get_ticks()

    def update(self):
        super().update()
        now = pygame.time.get_ticks()
        if self.aggro and now - self.last_summon_time > self.summon_cooldown:
            self.summon()
            self.last_summon_time = now

    def summon(self):
        from scripts.objects.particle import Particle
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.game.sprites.particles.append(
                Particle(self.rect.center, velocity, timer=40, color=COLOR_BLUE)
            )

        for _ in range(2):
            off_x = random.randint(-150, 150)
            off_y = random.randint(-150, 150)
            new_alien = AlienMinion(self.rect.centerx + off_x,
                                    self.rect.centery + off_y, self.ship, self.game)
            new_alien.aggro = True
            new_alien.in_formation = False
            self.game.sprites.aliens.add(new_alien)

class AlienMinion(Alien):
    def __init__(self, x, y, ship, game):
        super().__init__("cyan", x, y, ship, game, base_hp=150, base_damage=15)