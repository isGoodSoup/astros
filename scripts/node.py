from scripts.all_skills import Explorer
from scripts.skill import Skill


class SkillNode:
    def __init__(self, skill):
        self.skill = skill
        self.children = []
        self.parents = skill.requirements
        self.pos = (0, 0)

        explorer = Skill("Explorer", Explorer(), "01_explorer")

        navigator = Skill("Navigator", Explorer(), "02_navigator")
        navigator.requirements = [explorer]

        pass
