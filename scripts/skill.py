import pygame

from scripts.all_skills import Explorer, DamageBoost, Maniac, Madness, Survival, \
    Adventurer, Pilot, Tank, Tower, Fortified
from scripts.lang import local
from scripts.sheet import SpriteSheet
from scripts.utils import resource_path, legacy


class Skill:
    def __init__(self, name, ability, icon, description_key=None, max_level=10,
            visual_tiers=5):
        self.name = name
        self.ability = ability

        self.description_key = description_key

        self.level = 0
        self.max_level = max_level
        self.unlocked = False
        self.hovered = False

        self.parents = []
        self.children = []

        self.sheet = SpriteSheet(resource_path("assets/ui/skills/skill_frame.png"))
        self.cols = 7
        self.visual_tiers = visual_tiers

        self.frames = {
            "locked": self.sheet.get_frame(0, self.cols),
            "unlocked": self.sheet.get_frame(1, self.cols),
            "hover": self.sheet.get_frame(5, self.cols),
            "unlockable": self.sheet.get_frame(6, self.cols),
        }

        self.icon_image = pygame.transform.scale(
            pygame.image.load(resource_path(f"assets/ui/skills/{icon}.png")),
            (64, 64)
        )

        self.rect = self.frames["locked"].get_rect(topleft=(0, 0))

    @property
    def description(self):
        if self.description_key:
            return local.t(self.description_key)
        return None

    @legacy
    def is_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

    def get_visual_tier(self):
        if self.level <= 0:
            return None

        return min(self.visual_tiers - 1, (self.level - 1) * self.visual_tiers // self.max_level)

    def current_frame(self):
        if self.hovered:
            return self.frames["hover"]

        if self.unlocked:
            tier = self.get_visual_tier()
            if tier is None:
                return self.frames["unlocked"]

            return self.sheet.get_frame(1 + tier, self.cols)

        return self.frames["unlockable"]

class SkillManager:
    def __init__(self):
        self.skills = []

        self.skills = [
            Skill("Explorer", Explorer(), "01_explorer", "game.skill.explorer"),
            Skill("Berserk", DamageBoost(), "02_berserk", "game.skill.berserk"),
            Skill("Maniac", Maniac(), "02a_maniac", "game.skill.maniac"),
            Skill("Madness", Madness(), "02b_madness", "game.skill.madness"),
            Skill("Survivor", Survival(), "03_survivor", "game.skill.survivor"),
            Skill("Adventurer", Adventurer(), "03a_adventurer", "game.skill.adventurer"),
            Skill("Pilot", Pilot(), "03b_pilot", "game.skill.pilot"),
            Skill("Tank", Tank(), "04_tank", "game.skill.tank"),
            Skill("Tower", Tower(), "04a_tower", "game.skill.tower"),
            Skill("Fortified", Fortified(), "04b_fortified", "game.skill.fortified"),
        ]

    def can_unlock(self, skill, ship):
        return ship.perk_points > 0 and all(r.level > 0 for r in skill.parents)

    def unlock_or_upgrade(self, skill, ship):
        if ship.perk_points <= 0:
            return

        if not skill.unlocked:
            skill.unlocked = True
            skill.level = 1
        elif skill.level < skill.max_level:
            skill.level += 1

        ship.perk_points -= 1

        if skill.ability:
            skill.ability.apply(ship, skill.level)

    def get_unlocked(self):
        return [s for s in self.skills if s.unlocked]