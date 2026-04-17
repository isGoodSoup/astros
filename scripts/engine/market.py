import random
import pygame
from scripts.system.prices import MARKET_ITEMS

class MarketNode(pygame.sprite.Sprite):
    def __init__(self, item, pos):
        super().__init__()
        self.item = item
        self.image = item.image
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy()
        self.active = True

    def apply(self, game):
        self.item.apply(game.ship, game)


class Market:
    def __init__(self, game):
        self.nodes = pygame.sprite.Group()
        self.items = random.sample(MARKET_ITEMS, k=min(3, len(MARKET_ITEMS)))

        while len(self.items) < 3:
            self.items.append(random.choice(MARKET_ITEMS))

        for item in self.items:
            pos = pygame.Vector2(
                random.randint(200, game.screen_size[0] - 200),
                random.randint(200, game.screen_size[1] - 200)
            )
            self.nodes.add(MarketNode(item, pos)) # type: ignore

    def update(self, game):
        self.nodes.update()

    def check_purchase(self, game):
        hits = pygame.sprite.spritecollide(
            game.ship,
            self.nodes,
            False,
            collided=lambda s, u: s.hitbox.colliderect(u.rect)
        )

        return hits[0] if hits else None

    def purchase(self, node, game):
        if not node.active:
            return

        if game.ship.credits < node.item.price:
            return

        game.ship.credits -= node.item.price
        node.apply(game)

        node.kill()
        game.mixer.play(2)