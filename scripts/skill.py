from scripts.all_skills import *
from scripts.sheet import SpriteSheet
import pygame

class Skill:
    def __init__(self, name, ability, icon, description=None, max_level=5):
        self.name = name
        self.description = description
        self.ability = ability

        self.spritesheet = SpriteSheet("assets/ui/skills/skill_frame.png")
        cols = 7
        frame_width = self.spritesheet.sheet.get_width() // cols
        frame_height = self.spritesheet.sheet.get_height()

        self.frames = {
            "locked": self.spritesheet.get_image(0, frame_width, frame_height, 4, cols),
            "unlocked": self.spritesheet.get_image(1, frame_width, frame_height, 4, cols),
            "hover": self.spritesheet.get_image(6, frame_width, frame_height, 4, cols)
        }

        for lvl in range(1, max_level + 1):
            self.frames[f"level{lvl}"] = (self.spritesheet.get_image
                (lvl + 1, frame_width, frame_height, 4, cols))

        self.icon_image = pygame.transform.scale(pygame.image.load
            (f"assets/ui/skills/{icon}.png"), (64, 64))
        self.x = 0
        self.y = 0
        self.rect = self.frames["locked"].get_rect(topleft=(self.x, self.y))

        self.level = 0
        self.max_level = max_level
        self.unlocked = False
        self.hovered = False
        self.requirements = []

    def is_hovered(self, mouse):
        self.hovered = self.rect.collidepoint(mouse.get_pos())
        return self.hovered

    def is_unlocked(self):
        return self.unlocked

    def current_frame(self):
        if self.hovered:
            return self.frames["hover"]
        if self.level > 0:
            return self.frames.get(f"level{self.level}", self.frames["unlocked"])
        if self.unlocked:
            return self.frames["unlocked"]
        return self.frames["locked"]

class SkillManager:
    def __init__(self):
        self.skills = []
        self.add_skill(Skill("Explorer", Explorer(), "01_explorer"))
        self.add_skill(Skill("Beserk", DamageBoost(), "02_damage"))

    def add_skill(self, skill):
        self.skills.append(skill)

    def unlock(self, skill):
        if self.can_unlock(skill):
            skill.unlocked = True

    def can_unlock(self, skill):
        return all(req.level > 0 for req in skill.requirements)

    def upgrade(self, skill, ship):
        if ship.perk_points <= 0:
            return

        if skill.unlocked and skill.level < skill.max_level:
            skill.level += 1
            ship.perk_points -= 1
            if skill.ability:
                skill.ability.apply(ship, skill.level)

    def get_unlocked(self):
        return [s for s in self.skills if s.unlocked]