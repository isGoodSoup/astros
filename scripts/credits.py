
def update_credits(game, game_font):
    short_credits = format_number(game.ship.credits)
    formatted_credits = f"{short_credits}€$"
    game.credits = game_font.render(formatted_credits, True, (255, 200, 0))

def format_number(n):
    for unit, value in [("B", 1_000_000_000), ("M", 1_000_000), ("K", 1_000)]:
        if n >= value:
            short = n / value
            return f"{short:.1f}" if short >= 10 else f"{short:.2f}" + unit
    return str(n)