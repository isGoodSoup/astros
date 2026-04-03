import pygame


class Tutorial:
    def __init__(self):
        self.step = 0
        self.active = True
        self.completed = False
        self.timer = 0

    def update(self, game, delta):
        if self.step == 0:
            if game.ship.moving:
                self.step += 1

        elif self.step == 1:
            if len(game.projectiles) > 0:
                self.step += 1

        elif self.step == 2:
            if game.skill_tab.active:
                self.step += 1

        elif self.step == 3:
            if game.ship.gun != "beam":
                self.step += 1

        elif self.step == 4:
            self.timer += delta
            if self.timer > 5:
                self.step += 1

        elif self.step == 5:
            self.active = False
            game.tutorial_active = False

    def render(self, screen, font):
        if self.step == 0:
            text = font.render("Move your ship", True, (255, 255, 255))
            screen.blit(text, (pygame.display.Info().current_w // 2 - text.get_width() // 2,
                               pygame.display.Info().current_h - 100))

        elif self.step == 1:
            text = font.render("Press SPACE / A to shoot", True,(255, 255, 255))
            screen.blit(text, (pygame.display.Info().current_w // 2 - text.get_width() // 2,
                               pygame.display.Info().current_h - 100))

        elif self.step == 2:
            text = font.render("Press TAB / B for the Skill Tree", True,(255,255, 255))
            screen.blit(text, (pygame.display.Info().current_w // 2 - text.get_width() // 2,
                               pygame.display.Info().current_h - 100))

        elif self.step == 3:
            text = font.render("Press G / X to switch gun mode", True, (255, 255, 255))
            screen.blit(text, (pygame.display.Info().current_w // 2 - text.get_width() // 2,
                               pygame.display.Info().current_h - 100))

        elif self.step == 4:
            text = font.render("Survive.", True,(255, 255, 255))
            screen.blit(text, (pygame.display.Info().current_w // 2 - text.get_width() // 2,
                               pygame.display.Info().current_h - 100))