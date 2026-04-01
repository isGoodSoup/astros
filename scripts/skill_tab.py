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
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 10
        self.active = False

    def update(self, hud_padding):
        if self.active:
            target_x = (pygame.display.Info().current_w -
                        self.image.get_width() - hud_padding)
            if self.x > target_x:
                self.x -= self.speed
        else:
            if self.x < self.start_x:
                self.x += self.speed
        self.rect.topleft = (self.x, self.y)

    def render(self, screen, font, ship, skill_manager):
        screen.blit(self.image, self.rect)
        perk_points = font.render(f"Perk Points: {ship.perk_points}", True,
                                  (255, 255, 255))
        padding = 75
        screen.blit(perk_points, (self.x + padding, self.y + padding // 2))

        for i, skill in enumerate(skill_manager.skills):
            skill_icon = pygame.image.load(skill.icon)
            skill_icon = pygame.transform.scale(skill_icon, (64, 64))
            skill_frame = pygame.transform.scale(skill.frame, (64, 64))
            screen.blit(skill_icon, (self.width//2, self.y + padding + (i * 80)))
            screen.blit(skill_frame, (self.width//2, self.y + padding + (i * 80)))