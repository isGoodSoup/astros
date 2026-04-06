
def update_credits(game, game_font):
    short_credits = format_number(game.ship.credits)
    formatted_credits = f"{short_credits}€$"
    game.credits = game_font.render(formatted_credits, True, (255, 200, 0))

def format_number(n):
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.2f}K"
    else:
        return f"{n:.0f}"