from enum import Enum, auto
from scripts.engine.utils import resource_path

class Difficulty(Enum):
    TOURIST = auto()
    EXPLORER = auto()
    PILOT = auto()
    NIGHTMARE = auto()

class DifficultyOption:
    def __init__(self, context, difficulty, name, modifiers, icon=None):
        self.context = context
        self.local = context.local
        self.trait = difficulty
        self.name = self.local.t(f"game.difficulty.{name}")
        self.modifiers = modifiers
        self.icon = resource_path(f"assets/difficulties/{icon}.png")

class DifficultyPool:
    def __init__(self, context):
        self.options = [
            DifficultyOption(context, Difficulty.TOURIST, "tourist",
                             {"hp_mult": 1.5, "damage_mult": 0.75}, "tourist"),
            DifficultyOption(context, Difficulty.EXPLORER, "explorer",
                             {"hp_mult": 1.0, "damage_mult": 1.0}, "explorer"),
            DifficultyOption(context, Difficulty.PILOT, "pilot",
                             {"hp_mult": 0.8, "damage_mult": 1.2}, "pilot"),
            DifficultyOption(context, Difficulty.NIGHTMARE, "nightmare",
                             {"hp_mult": 0.6, "damage_mult": 1.5}, "nightmare"),
        ]