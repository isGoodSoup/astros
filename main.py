import random

import pygame as pg
from pygame.display import toggle_fullscreen

from explode import Explosion
from meteor import Meteor
from proj import Projectile
from ship import Ship
from soundlib import load_sounds, load_ost
from sprites import SpriteSheet

cols = 20
animation_cooldown = 100

class Menu:
    def __init__(self):
        pg.init()
        pg.font.init()
        self.screen_size = (int(pg.display.Info().current_w / 4),
                            int(pg.display.Info().current_h / 1.5))
        self.screen = pg.display.set_mode(self.screen_size, pg.SCALED, vsync=1)
        self.game_font = pg.font.Font("assets/ui/PressStart2P.ttf", 56)
        self.text_font = pg.font.Font("assets/ui/PressStart2P.ttf", 24)
        pg.display.set_caption("Astros")
        self.clock = pg.time.Clock()
        self.running = True

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        game = Game(self.screen_size)
                        game.run(self.running, self.clock, self.screen,
                                 self.screen_size, self.text_font)
                    elif event.key == pg.K_ESCAPE:
                        self.running = False

            self.screen.fill((0, 0, 0))
            title = self.game_font.render("ASTROS", True, (255, 220, 50))
            start = self.text_font.render("Press Enter", True,"WHITE")
            self.screen.blit(title, (self.screen_size[0]//2 - title.get_width()//2, 100))
            self.screen.blit(start, (self.screen_size[0]//2 - start.get_width()//2, 500))
            pg.display.update()
            self.clock.tick(60)

class Game:
    def __init__(self, screen_size):
        self.fps = 60
        self.frame = 0
        self.scale = 3
        self.sounds = load_sounds()
        self.theme = load_ost()
        pg.mixer.music.play(-1)
        self.projectiles = pg.sprite.Group()
        self.meteors = pg.sprite.Group()
        self.explosions = pg.sprite.Group()

        self.sprite_sheet = SpriteSheet("assets/ship.png")
        framew = self.sprite_sheet.sheet.get_width() // cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         framew, frameh, columns=cols)
        self.ship_alive = True
        self.ship_x = screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = screen_size[1] // 2 + 200

        self.frames_movement = []
        self.frames = []
        for i in range(cols):
            img = self.sprite_sheet.get_image(i, framew, frameh, scale=self.scale,columns=cols)
            self.frames.append(img)

        self.frames_movement = self.frames[0:8]
        self.frames_shooting = self.frames[8:12]
        self.frame_idle = self.frames[12]
        self.frame_explode = self.frames[13:20]

        self.stars = [[random.randint(0, screen_size[0]),
                       random.randint(0, screen_size[1]),
                       random.randint(1, 3)] for _ in range(100)]
        self.last_update = pg.time.get_ticks()

        self.last_meteor_spawn = 0
        self.meteor_spawn_interval = 800
        self.last_shot_time = 0
        self.shot_cooldown = 300
        self.score = 0
        self.game_over = False

        self.debugging = False
        self.cursor = True

    def run(self, running, clock, screen, screen_size, game_font):
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    if self.game_over and event.key == pg.K_r:
                        self.reset(screen_size)
                    if event.key == pg.K_F2:
                        self.debug()
                    if event.key == pg.K_F1:
                        toggle_fullscreen()
                        self.toggle_cursor()

            clock.tick(self.fps)
            screen.fill((0,0,0))

            for i in self.stars:
                pg.draw.circle(screen, (255, 255, 255),
                                   (int(i[0]), int(i[1])), i[2])
                i[1] += 2
                if i[1] > screen_size[1]:
                    i[1] = 0
                    i[0] = random.randint(0, screen_size[0])

            current_time = pg.time.get_ticks()
            if current_time - self.last_meteor_spawn > self.meteor_spawn_interval:
                self.last_meteor_spawn = current_time
                for _ in range(random.randint(1, 4)):
                    for _ in range(10):
                        new_meteor = Meteor(screen_size[0], min_y=-200,max_y=-50)
                        too_close = any(abs(new_meteor.rect.y - m.rect.y) < 60 for m in self.meteors)
                        if not too_close:
                            self.meteors.add(new_meteor) # type: ignore
                            break

            current_time = pg.time.get_ticks()
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
            self.meteors.draw(screen)
            if self.debugging:
                for i in self.meteors:
                    pg.draw.rect(screen, (255, 0, 0),i.hitbox, 2)

            if self.ship_alive:
                self.ship.image = img
                screen.blit(self.ship.image, [self.ship_x, self.ship_y])
                if self.debugging:
                    pg.draw.rect(screen, (255, 0, 0), self.ship.hitbox,2)
            if not self.game_over:
                key_pressed = pg.key.get_pressed()
                if key_pressed[pg.K_LEFT] and self.ship_x > 0:
                    self.ship_x -= self.ship.velocity
                    self.ship.moving = True
                if key_pressed[pg.K_RIGHT] and self.ship_x < \
                        screen_size[0] - img.get_width():
                    self.ship_x += self.ship.velocity
                    self.ship.moving = True
                if key_pressed[pg.K_UP] and self.ship_y > 0:
                    self.ship_y -= self.ship.velocity
                    self.ship.moving = True
                if (key_pressed[pg.K_DOWN] and self.ship_y <
                        screen_size[1] - self.ship.image.get_height()):
                    self.ship_y += self.ship.velocity
                    self.ship.moving = False

                if self.ship_alive:
                    if key_pressed[pg.K_SPACE] and current_time - self.last_shot_time >= self.shot_cooldown:
                        self.last_shot_time = current_time
                        self.ship.state = "shoot"
                        projectile = Projectile(
                            self.ship_x + img.get_width() // 2,
                            self.ship_y)
                        self.projectiles.add(projectile)  # type: ignore
                        self.sounds[0].play()
                    elif self.ship.moving:
                        self.ship.state = "move"
                    else:
                        self.ship.state = "idle"

                self.projectiles.update()
                self.projectiles.draw(screen)

                if self.ship_alive:
                    self.ship.update_position(self.ship_x, self.ship_y)
                meteor_hit = pg.sprite.spritecollideany(self.ship, self.meteors, # type: ignore
                                                            collided=lambda s, m: s.hitbox.colliderect(m.rect))
                if meteor_hit and not self.game_over:
                    explosion = Explosion(self.ship_x + img.get_width() // 2,
                                          self.ship_y + img.get_height() // 2,
                                          self.frame_explode)
                    self.explosions.add(explosion)  # type: ignore
                    meteor_hit.kill()
                    self.sounds[1].play()
                    self.ship.kill()
                    self.ship_alive = False

                    pg.mixer.music.stop()
                    self.game_over = True

                hits = pg.sprite.groupcollide(self.projectiles,
                                                  self.meteors,
                                                  True, False)
                for meteor in hits.values():
                    explosion = Explosion(meteor[0].rect.centerx,
                                          meteor[0].rect.centery,
                                          self.frame_explode)
                    self.explosions.add(explosion)  # type: ignore
                    meteor[0].kill()
                    self.sounds[1].play()
                    self.score += 10

            self.explosions.update()
            self.explosions.draw(screen)

            score_text = f"{self.score:05}"
            text_surface = game_font.render(score_text, True, "WHITE")
            screen.blit(text_surface, [screen_size[0] - 160, 50])
            pg.display.update()

            if self.game_over:
                game_over = game_font.render("GAME OVER", True, "RED")
                screen.blit(game_over,[screen_size[0] // 2 - 150,screen_size[1] // 2])
        pg.quit()

    def reset(self, screen_size):
        self.projectiles.empty()
        self.meteors.empty()
        self.explosions.empty()
        framew = self.sprite_sheet.sheet.get_width() // cols
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         self.sprite_sheet.sheet.get_width(),
                         self.sprite_sheet.sheet.get_height(), columns=4)
        self.ship_alive = True
        self.ship_x = screen_size[0] // 2 - framew // 2 - 25
        self.ship_y = screen_size[1] // 2 + 200

        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.last_meteor_spawn = 0
        self.last_shot_time = 0
        self.score = 0
        self.game_over = False
        pg.mixer.music.play(-1)

    def debug(self):
        if self.debugging:
            self.debugging = False
            return

        if not self.debugging:
            self.debugging = True
            return

    def toggle_cursor(self):
        self.cursor = not self.cursor
        pg.mouse.set_visible(self.cursor)

if __name__ == '__main__':
    menu = Menu()
    menu.run()