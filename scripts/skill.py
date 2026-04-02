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
            "unlocked1": self.spritesheet.get_image(1, frame_width, frame_height, 4, cols),
            "unlocked2": self.spritesheet.get_image(2, frame_width, frame_height, 4, cols),
            "unlocked3": self.spritesheet.get_image(3, frame_width, frame_height, 4, cols),
            "unlocked4": self.spritesheet.get_image(4, frame_width, frame_height, 4, cols),
            "hover": self.spritesheet.get_image(5, frame_width, frame_height,4, cols),
            "unlockable": self.spritesheet.get_image(6, frame_width, frame_height,4, cols)
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

        self.pos = (0, 0)
        self.parents = []
        self.children = []

    def is_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def is_unlocked(self):
        return self.unlocked

    def current_frame(self):
        if self.hovered:
            return self.frames["hover"]

        if self.unlocked:
            if self.level > 0:
                return self.frames.get(f"unlocked{self.level}", self.frames["unlocked1"])
            return self.frames["unlocked1"]

        if all(parent.level > 0 for parent in self.parents):
            return self.frames["unlockable"]

        return self.frames["locked"]

class SkillManager:
    def __init__(self):
        self.skills = []

    def add_skill(self, skill):
        self.skills.append(skill)

    def can_unlock(self, skill, ship):
        return ship.perk_points > 0 and all(req.level > 0 for req in skill.parents)

    def unlock_or_upgrade(self, skill, ship):
        if ship.perk_points <= 0:
            return

        if not skill.unlocked:
            if all(req.level > 0 for req in skill.parents):
                skill.unlocked = True
                skill.level = 1
                ship.perk_points -= 1
                if skill.ability:
                    skill.ability.apply(ship, skill.level)
        elif skill.level < skill.max_level:
            skill.level += 1
            ship.perk_points -= 1
            if skill.ability:
                skill.ability.apply(ship, skill.level)

    def get_unlocked(self):
        return [s for s in self.skills if s.unlocked]

    def build_tree(self, skill_tab):
        explorer = Skill("Explorer", Explorer(), "01_explorer")
        berserk = Skill("Berserk", DamageBoost(), "02_berserk")
        maniac = Skill("Maniac", Maniac(), "02a_maniac")

        survivor = Skill("Survivor", Survival(), "03_survivor")
        adventurer = Skill("Adventurer", Adventurer(), "03a_adventurer")

        tank = Skill("Tank", Tank(), "04_tank")

        explorer.parents = []
        berserk.parents = [explorer]
        maniac.parents = [berserk]
        adventurer.parents = [survivor]

        survivor.parents = [explorer]

        tank.parents = [explorer]

        explorer.children = [berserk, survivor, tank]
        berserk.children = [maniac]
        survivor.children = [adventurer]

        explorer.pos = (skill_tab.padding + 180, skill_tab.padding)
        padding = 80
        berserk.pos = (explorer.pos[0] - 120, explorer.pos[1] + padding)
        survivor.pos = (explorer.pos[0], explorer.pos[1] + padding)
        tank.pos = (explorer.pos[0] + 120, explorer.pos[1] + padding)

        maniac.pos = (berserk.pos[0], berserk.pos[1] + padding)
        adventurer.pos = (survivor.pos[0], berserk.pos[1] + padding)
        self.skills = [explorer, berserk, survivor, tank, maniac, adventurer]