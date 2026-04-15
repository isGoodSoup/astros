from typing import overload


class Ability:
    def apply(self, ship, level):
        pass

    def apply_on(self, game, ship):
        pass

    def on_kill(self, ship, level):
        pass