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
        self.nodes = [

        ]

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
        padding = 75
        perk_points = font.render(f"Perks: {ship.perk_points}", True,
                                  (255, 255, 255))
        screen.blit(perk_points, (self.x + padding, self.y + padding // 2))

        for i, skill in enumerate(skill_manager.skills):
            y_pos = self.y + padding + (i * 80)
            x_pos = self.x + self.width // 2
            skill.rect.topleft = (x_pos, y_pos)
            skill.is_hovered(pygame.mouse)
            frame = pygame.transform.scale(skill.current_frame(), (64, 64))
            screen.blit(frame, (x_pos, y_pos))
            screen.blit(skill.icon_image, (x_pos, y_pos))