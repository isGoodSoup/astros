from scripts.all_traits import DoubleBoss
from scripts.lang import local


class Trait:
    def __init__(self, name, description, ability):
        self.name = name
        self.description = description
        self.ability = ability

    def apply(self, ship, level):
        self.ability.apply(ship, level)

class TraitManager:
    def __init__(self):
        self.available_traits = [
            Trait(local.t('game.trait.name.boss'),
                  local.t('game.trait.desc.boss'), DoubleBoss())
        ]