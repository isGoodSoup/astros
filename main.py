import random

import pygame

from explode import Explosion
from meteor import Meteor
from proj import Projectile
from ship import Ship
from sprites import SpriteSheet

cols = 20
animation_cooldown = 100

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen_size = (int(pygame.display.Info().current_w / 4),
                            int(pygame.display.Info().current_h / 1.5))
        self.screen = pygame.display.set_mode(self.screen_size, pygame.SCALED, vsync=1)
        self.game_font = pygame.font.Font("assets/ui/PressStart2P.ttf", 24)
        pygame.display.set_caption("Astros")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.frame = 0
        self.scale = 3
        self.projectiles = pygame.sprite.Group()
        self.meteors = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()
        self.sprite_sheet = SpriteSheet("assets/ship.png")
        framew = self.sprite_sheet.sheet.get_width() // cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         self.sprite_sheet.sheet.get_width(),
                         self.sprite_sheet.sheet.get_height(), columns=4)
        self.ship_alive = True
        self.ship_x = self.screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = self.screen_size[1] // 2 + 200

        self.frames_movement = []
        self.frames = []
        for i in range(cols):
            img = self.sprite_sheet.get_image(i, framew, frameh, scale=self.scale,columns=cols)
            self.frames.append(img)

        self.frames_movement = self.frames[0:8]
        self.frames_shooting = self.frames[8:12]
        self.frame_idle = self.frames[12]
        self.frame_explode = self.frames[13:20]

        self.stars = [[random.randint(0, self.screen_size[0]),
                       random.randint(0, self.screen_size[1]),
                       random.randint(1, 3)] for _ in range(100)]
        self.last_update = pygame.time.get_ticks()

        self.last_meteor_spawn = 0
        self.meteor_spawn_interval = 800
        self.last_shot_time = 0
        self.shot_cooldown = 300
        self.score = 0

    def run(self):
        while self.running:
            self.clock.tick(self.fps)
            self.screen.fill((0,0,0))

            for i in self.stars:
                pygame.draw.circle(self.screen, (255, 255, 255),
                                   (int(i[0]), int(i[1])), i[2])
                i[1] += 2
                if i[1] > self.screen_size[1]:
                    i[1] = 0
                    i[0] = random.randint(0, self.screen_size[0])

            current_time = pygame.time.get_ticks()
            if current_time - self.last_meteor_spawn > self.meteor_spawn_interval:
                self.last_meteor_spawn = current_time
                for _ in range(random.randint(1, 4)):
                    for _ in range(10):
                        new_meteor = Meteor(self.screen_size[0], min_y=-200,
                                            max_y=-50)
                        too_close = any(
                            abs(new_meteor.rect.y - m.rect.y) < 60 for m in
                            self.meteors)
                        if not too_close:
                            self.meteors.add(new_meteor) # type: ignore
                            break

            current_time = pygame.time.get_ticks()
            if current_time - self.last_update >= animation_cooldown:
                self.last_update = current_time
                self.frame += 1
                if self.frame >= len(self.frames):
                    self.frame = 0

            if self.ship.state == "move":
                img = self.frames_movement[
                    self.frame % len(self.frames_movement)]
            elif self.ship.state == "shoot":
                img = self.frames_shooting[
                    self.frame % len(self.frames_shooting)]
            else:
                img = self.frame_idle

            self.meteors.update()
            self.meteors.draw(self.screen)

            if self.ship_alive:
                self.ship.image = img
                self.screen.blit(self.ship.image, [self.ship_x, self.ship_y])

            key_pressed = pygame.key.get_pressed()
            if key_pressed[pygame.K_LEFT] and self.ship_x > 0:
                self.ship_x -= self.ship.velocity
                self.ship.moving = True
            if key_pressed[pygame.K_RIGHT] and self.ship_x < self.screen_size[0] - img.get_width():
                self.ship_x += self.ship.velocity
                self.ship.moving = True
            if key_pressed[pygame.K_UP] and self.ship_y > 0:
                self.ship_y -= self.ship.velocity
                self.ship.moving = True
            if (key_pressed[pygame.K_DOWN] and self.ship_y < self.screen_size[1]
                    - self.ship.image.get_height()):
                self.ship_y += self.ship.velocity
                self.ship.moving = False

            if key_pressed[
                pygame.K_SPACE] and current_time - self.last_shot_time >= self.shot_cooldown:
                self.last_shot_time = current_time
                self.ship.state = "shoot"
                projectile = Projectile(self.ship_x + img.get_width() // 2,self.ship_y)
                self.projectiles.add(projectile)  # type: ignore
            elif self.ship.moving:
                self.ship.state = "move"
            else:
                self.ship.state = "idle"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.projectiles.update()
            self.projectiles.draw(self.screen)

            if self.ship_alive:
                self.ship.update_position(self.ship_x, self.ship_y)
            meteor_hit = pygame.sprite.spritecollideany(self.ship, self.meteors)  # type: ignore
            if meteor_hit:
                explosion = Explosion(self.ship_x + img.get_width() // 2,
                                      self.ship_y + img.get_height() // 2,
                                      self.frame_explode)
                self.explosions.add(explosion)  # type: ignore
                meteor_hit.kill()
                self.ship.kill()
                self.ship_alive = False

            hits = pygame.sprite.groupcollide(self.projectiles, self.meteors,
                                              True, False)
            for meteor in hits.values():
                explosion = Explosion(meteor[0].rect.centerx,
                                      meteor[0].rect.centery,
                                      self.frame_explode)
                self.explosions.add(explosion)  # type: ignore
                meteor[0].kill()
                self.score += 1

            self.explosions.update()
            self.explosions.draw(self.screen)

            text_surface = self.game_font.render(str(self.score), True, "WHITE")
            self.screen.blit(text_surface, [self.screen_size[0]/2, 100])
            pygame.display.update()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()