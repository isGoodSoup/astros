import pygame

class SkillTab(pygame.sprite.Sprite):
    def __init__(self, scale=4):
        super().__init__()
        self.image = pygame.image.load("assets/ui/skill_tab.png")
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * scale,
            self.image.get_height() * scale))
        self.rect = self.image.get_rect()
        self.start_x = pygame.display.Info().current_w - 32
        self.x = self.start_x
        self.y = (pygame.display.Info().current_h // 2 -
                  self.image.get_height() // 2) - 75
        self.speed = 10
        self.active = False

    def update(self):
        if self.active:
            target_x = pygame.display.Info().current_w - self.image.get_width() - 50
            if self.x > target_x:
                self.x -= self.speed
        else:
            if self.x < self.start_x:
                self.x += self.speed
        self.rect.topleft = (self.x, self.y)

    def render(self, screen, font, ship):
        screen.blit(self.image, self.rect)
        perk_points = font.render(f"Perk Points: {ship.perk_points}", True,(255, 255, 255))
        padding = 75
        screen.blit(perk_points, (self.x + padding, self.y + padding//2))
