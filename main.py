import random

import pygame

from ship import Ship
from sprites import SpriteSheet

cols = 13
animation_cooldown = 100

class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = (pygame.display.Info().current_w/4,
                            pygame.display.Info().current_h/1.5)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.SCALED, vsync=1)
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.frame = 0
        self.scale = 3
        self.sprite_sheet = SpriteSheet("assets/ship.png")
        framew = self.sprite_sheet.sheet.get_width() // cols
        frameh = self.sprite_sheet.sheet.get_height()
        self.ship = Ship(self.sprite_sheet, 0, 0, self.frame,
                         self.sprite_sheet.sheet.get_width(),
                         self.sprite_sheet.sheet.get_height(), columns=4)
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

        self.stars = [[random.randint(0, int(self.screen_size[0])),
                       random.randint(0, int(self.screen_size[1])),
                       random.randint(1, 3)] for _ in range(100)]
        self.last_update = pygame.time.get_ticks()

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
                    i[0] = random.randint(0, int(self.screen_size[0]))

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

            self.screen.blit(img, [self.ship_x, self.ship_y])
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
            if key_pressed[pygame.K_DOWN] and self.ship_y < self.screen_size[1] - self.ship.sprite.get_height():
                self.ship_y += self.ship.velocity
                self.ship.moving = False

            if key_pressed[pygame.K_SPACE]:
                self.ship.state = "shoot"
            elif self.ship.moving:
                self.ship.state = "move"
            else:
                self.ship.state = "idle"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.update()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()