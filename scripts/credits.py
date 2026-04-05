
def update_credits(game, game_font):
    formatted_credits = f"{game.ship.credits:,.0f}".replace(',', '.') + "€$"
    game.credits = game_font.render(formatted_credits, True, (255, 200, 0))