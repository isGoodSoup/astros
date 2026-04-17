
import scripts.system.assets as assets
from scripts.system.constants import SHIP_AMMO


class MarketItem:
    def __init__(self, item_type, price, stock, image):
        self.type = item_type
        self.price = price
        self.stock = stock
        self.image = image

    def apply(self, ship, game):
        if self.type == "ammo":
            for ammo_type in SHIP_AMMO:
                ship.guns_ammo[ammo_type] += 100

        elif self.type == "repairs":
            ship.hitpoints = min(ship.max_hitpoints, ship.hitpoints + 100)
            ship.shield = min(ship.max_shield, ship.shield + 100)

        elif self.type == "damage":
            ship.damage *= 1.05

def build_market():
    return [
        MarketItem("ammo", 50, 200, assets.MARKET_AMMO),
        MarketItem("repairs", 2000, 2, assets.MARKET_REPAIRS),
        MarketItem("damage", 3000, 1, assets.MARKET_DAMAGE_BOOST)
    ]