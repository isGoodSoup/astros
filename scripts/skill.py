from scripts.all_skills import *
from scripts.sheet import SpriteSheet
import pygame

from scripts.utils import resource_path


class Skill:
    def __init__(self, name, ability, icon, description=None, max_level=5):
        self.name = name
        self.description = description
        self.ability = ability

        self.spritesheet = SpriteSheet(resource_path("assets/ui/skills/skill_frame.png"))
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
            (resource_path(f"assets/ui/skills/{icon}.png")), (64, 64))
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

    def set_description(self, description):
        self.description = description

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
                return self.frames.get(f"unlocked{self.level}",self.frames["unlocked1"])
            return self.frames["unlocked1"]

        return self.frames["unlockable"]

class SkillManager:
    def __init__(self):
        self.skills = []

        explorer = Skill("Explorer", Explorer(), "01_explorer")
        berserk = Skill("Berserk", DamageBoost(), "02_berserk")
        maniac, madness = (Skill("Maniac", Maniac(), "02a_maniac"),
                           Skill("Madness", Madness(), "02b_madness"))

        survivor = Skill("Survivor", Survival(), "03_survivor")
        adventurer, pilot = Skill("Adventurer", Adventurer(),
                                  "03a_adventurer"), Skill("Pilot", Pilot(), "03b_pilot")

        tank = Skill("Tank", Tank(), "04_tank")
        tower, fortified = (Skill("Tower", Tower(), "04a_tower"),
                            Skill("Fortified", Fortified(), "04b_fortified"))

        explorer.set_description("Enhance your ship’s resilience, increasing both "
                                 "hull integrity and shield capacity. The added bulk "
                                 "slightly reduces maneuverability.")

        berserk.set_description("Embrace raw destructive power at the cost of survivability. "
                                "Your weapons hit harder, but your defenses suffer.")

        maniac.set_description("Enter a manic combat state, dramatically increasing "
                               "critical chance for a short time. Once the frenzy ends, "
                               "your weapons require time to recover.")

        madness.set_description("Channel chaotic energy to amplify critical strikes, "
                                "sacrificing defensive stability in the process.")

        survivor.set_description("Prioritize survival with stronger shields and "
                                 "improved evasive maneuvers, at the expense of "
                                 "offensive capability.")

        adventurer.set_description("Enhance agility and speed to outmaneuver threats, "
                                   "sacrificing shield strength for mobility.")

        pilot.set_description("Expert piloting enhances survivability and evasiveness, "
                              "though offensive output is modestly reduced.")

        tank.set_description("Transform your ship into a heavily armored fortress. "
                             "The immense durability comes at the cost of agility and "
                             "maneuverability.")

        tower.set_description("Become an immovable bastion. Remaining stationary "
                              "significantly boosts shield capacity, but structural "
                              "reinforcements hinder mobility.")

        fortified.set_description("Reinforce your defenses to mitigate incoming damage. "
                                  "However, the heavy fortifications slow shield recovery.")

        self.skills = [explorer, berserk, survivor, tank, maniac,
                       madness, adventurer, pilot, tower, fortified]

    def add_skill(self, skill):
        self.skills.append(skill)

    def can_unlock(self, skill, ship):
        return ship.perk_points > 0 and all(req.level > 0 for req in skill.parents)

    def unlock_or_upgrade(self, skill, ship):
        if ship.perk_points <= 0:
            return

        if not skill.unlocked:
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