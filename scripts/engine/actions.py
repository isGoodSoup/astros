
def create_actions():
    return {
        "move": (0.0, 0.0),
        "shoot": False,
        "secondary": False,
        "pause": False,
        "switch_weapon": False,

        # future UI (don’t use yet)
        "ui_next": False,
        "ui_prev": False,
        "ui_confirm": False,
    }