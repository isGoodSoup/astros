
def update_credits(game, game_font):
    game.credits = game_font.render(f"{game.ship.credits}€$", True,
                                    (255, 200, 0))