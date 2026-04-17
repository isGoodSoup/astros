import random
import pygame

from scripts.system.constants import COLOR_LIGHT_ORANGE, COLOR_WHITE

MARKET_ITEM_SCALE = 4
MARKET_ITEM_SIZE = 64

class MarketNode(pygame.sprite.Sprite):
    def __init__(self, item, pos):
        super().__init__()
        self.item = item
        raw = item.image
        scaled = pygame.transform.scale(
            raw,
            (raw.get_width() * MARKET_ITEM_SCALE,
             raw.get_height() * MARKET_ITEM_SCALE)
        )
        self.image = scaled
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.inflate(20, 20)
        self.active = True

    def apply(self, game):
        self.item.apply(game.ship, game)


class Market:
    def __init__(self, game, items):
        self.nodes = pygame.sprite.Group()
        self.items = random.sample(items, k=min(2, len(items)))

        while len(self.items) < 3:
            self.items.append(random.choice(items))

        sw, sh = game.screen_size
        count = len(self.items)
        spacing = sw // (count + 1)
        y = sh // 2

        for i, item in enumerate(self.items):
            x = spacing * (i + 1)
            self.nodes.add(MarketNode(item, (x, y)))  # type: ignore

        self.font = game.font.get_font()

    def update(self, game):
        self.nodes.update()

    def draw(self, screen, game):
        sw, sh = game.screen_size

        dim = pygame.Surface((sw, sh))
        dim.fill((0, 0, 0))
        dim.set_alpha(160)
        screen.blit(dim, (0, 0))

        self.nodes.draw(screen)

        for node in self.nodes:
            name_surf = self.font.render(game.local.t(node.item.type.upper()), True, COLOR_WHITE)
            price_surf = self.font.render(f"${node.item.price}", True, COLOR_LIGHT_ORANGE)
            name_rect = name_surf.get_rect(centerx=node.rect.centerx,
                                           top=node.rect.bottom + 10)
            price_rect = price_surf.get_rect(centerx=node.rect.centerx,
                                             top=name_rect.bottom + 6)
            screen.blit(name_surf, name_rect)
            screen.blit(price_surf, price_rect)

    def check_click(self, pos):
        for node in self.nodes:
            if node.rect.collidepoint(pos):
                return node
        return None

    def purchase(self, node, game):
        if not node.active:
            return

        if game.ship.credits < node.item.price:
            return

        game.ship.credits -= node.item.price
        node.apply(game)

        node.kill()
        game.mixer.play(2)
