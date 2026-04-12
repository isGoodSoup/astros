import pygame

from scripts.all_traits import DoubleTrouble, GlassReactor, Panomium
from scripts.lang import local
from scripts.settings import (COLOR_WHITE, COLOR_LIGHT_ORANGE,
                              TRAIT_CARD_SIZE, SCALE)
from scripts.utils import resource_path, wrap_text


class Trait:
    def __init__(self, name, description, icon, ability):
        self.name = name
        self.description = description
        self.icon = resource_path(f"assets/ui/traits/trait_{icon}.png")
        self.ability = ability

    def apply(self, ship, level):
        self.ability.apply(ship, level)


class TraitGridSquare:
    def __init__(self, option, font):
        self.option = option
        self.font = font

        self.icon = pygame.image.load(option.icon).convert_alpha()
        self.icon = pygame.transform.scale(self.icon, (self.icon.get_width() * SCALE,
                                                       self.icon.get_height() * SCALE))
        self.is_selected = False

    def set_selected(self, selected):
        self.is_selected = selected

    def draw(self, screen, pos):
        x, y = pos
        rect = pygame.Rect(0, 0, TRAIT_CARD_SIZE, TRAIT_CARD_SIZE)
        rect.center = (x, y)

        border = COLOR_LIGHT_ORANGE if self.is_selected else COLOR_WHITE
        pygame.draw.rect(screen, border, rect, 4, border_radius=16)

        screen.blit(self.icon, self.icon.get_rect(center=(rect.centerx,
                                                          rect.top + 100)))

        name_text = wrap_text(self.option.name, self.font, rect.width)
        y_offset = rect.top + 150
        for line in name_text:
            surf = self.font.render(line, True, COLOR_LIGHT_ORANGE)
            screen.blit(surf, (rect.centerx - surf.get_width() // 2, y_offset))
            y_offset += 40

class TraitOption:
    def __init__(self, trait, meta=None):
        self.trait = trait
        self.meta = meta or {}

    @property
    def name(self):
        return self.trait.name

    @property
    def description(self):
        return self.trait.description

    @property
    def icon(self):
        return self.trait.icon

    def apply(self, ship, level):
        self.trait.apply(ship, level)

class TraitPool:
    def __init__(self):
        self.traits = [
            Trait(local.t('game.trait.name.boss'),
                  local.t('game.trait.desc.boss'), "double_trouble",DoubleTrouble()),
            Trait(local.t('game.trait.name.glass'),
                  local.t('game.trait.desc.glass'), "glass_reactor", GlassReactor()),
            Trait(local.t('game.trait.name.panonium'),
                  local.t('game.trait.desc.panonium'), "pandemonium", Panomium())
        ]

    def roll(self, count=3):
        return self.traits[:count]