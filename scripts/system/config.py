import json

from scripts.system.constants import *

def save_config(game):
    config_data = {
        "music_volume": game.mixer.music_volume,
        "sfx_volume": game.mixer.sfx_volume,
        "play_sound": game.state.play_sound,
        "screen_shake": game.state.screen_shake_amount,
        "rumble": game.state.can_rumble,
        "show_controls": game.state.can_show_controls,
        "show_hud": game.state.can_show_hud,
        "show_subtitles": game.state.show_subtitles,
        "high_score": game.state.high_score,
        "language": game.state.current_lang,
        "difficulty": game.state.difficulty.name,
    }
    with open(game.config_path, "w") as f:
        json.dump(config_data, f, indent=INDENTS)


def load_config(game):
    if os.path.exists(game.config_path):
        try:
            with open(game.config_path, "r") as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            config_data = {}

        game.mixer.music_volume = config_data.get("music_volume", MUSIC_VOLUME)
        game.mixer.sfx_volume = config_data.get("sfx_volume", SFX_VOLUME)
        game.state.play_sound = config_data.get("play_sound", True)
        game.state.screen_shake_amount = config_data.get("screen_shake", 0.4)
        game.state.can_rumble = config_data.get("rumble", True)
        game.state.can_show_controls = config_data.get("show_controls", True)
        game.state.can_show_hud = config_data.get("show_hud", True)
        game.state.show_subtitles = config_data.get("show_subtitles", False)
        game.state.high_score = config_data.get("high_score", 0)
        game.state.current_lang = config_data.get("language", "en")
        from scripts.engine.difficulty import Difficulty
        game.state.difficulty = Difficulty[config_data.get("difficulty", "EXPLORER")]