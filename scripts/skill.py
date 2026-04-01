from scripts.all_skills import Explorer
from scripts.sheet import SpriteSheet


class Skill:
    def __init__(self, name, ability, icon, description=None):
        self.name = name
        self.description = description
        self.ability = ability
        self.spritesheet = SpriteSheet("assets/ui/skills/skill_frame.png")

        cols = 7
        self.single_frame = 0
        self.frame = self.spritesheet.get_image(self.single_frame,
            self.spritesheet.sheet.get_width() // cols,
            self.spritesheet.sheet.get_height(), 4, cols)
        self.icon = f"assets/ui/skills/{icon}.png"

        self.level = 0
        self.max_level = 5
        self.unlocked = False
        self.hovered = False

        self.requirements = []

class SkillManager:
    def __init__(self):
        self.skills = []
        self.add_skill(Skill("Explorer", Explorer(), "01_explorer"))

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