
import scripts.system.assets as assets

class MarketItem:
    def __init__(self, item_type, price, stock, image):
        self.type = item_type
        self.price = price
        self.stock = stock
        self.image = image

MARKET_ITEMS = [
    MarketItem("ammo", 50, 200, assets.MARKET_AMMO),
    MarketItem("repairs", 2000, 2, assets.MARKET_REPAIRS),
]