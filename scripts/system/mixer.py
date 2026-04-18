import pygame

from scripts.system.constants import FADE_MS, SFX_VOLUME, MUSIC_VOLUME, \
    SETTINGS_DEFINITION
from scripts.system.soundlib import load_sounds, load_ost
from scripts.engine.utils import _get_setting_target
from scripts.system.config import save_config

class Mixer:
    def __init__(self, game=None):
        self.game = game
        self.sounds = load_sounds()
        self.ost = load_ost()
        self.music_volume = MUSIC_VOLUME
        self.sfx_volume = SFX_VOLUME
        self.current_track = None

        self.playlist = []
        self.playlist_index = 0
        self.loop_playlist = False

    def play(self, sfx):
        pygame.mixer.Sound.set_volume(self.sounds[sfx], self.sfx_volume)
        pygame.mixer.Sound.play(self.sounds[sfx])

    def play_music(self, track_name, loop=True, fade_ms=FADE_MS):
        pygame.mixer.music.set_volume(self.music_volume)
        if self.current_track == track_name:
            return

        if track_name not in self.ost:
            raise ValueError(f"Track '{track_name}' not found in OST.")

        pygame.mixer.music.fadeout(fade_ms)
        pygame.mixer.music.load(self.ost[track_name])
        pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)

        if self.game.state.show_subtitles:
            self.game.subtitle.add_subtitle(f"♪ {track_name}")

        self.current_track = track_name
        self.playlist = []
        self.playlist_index = 0
        self.loop_playlist = False

    def queue(self, track_names, loop=True, fade_ms=FADE_MS):
        if isinstance(track_names, str):
            track_names = [track_names]

        for name in track_names:
            if name not in self.ost:
                raise ValueError(f"Track '{name}' not found in OST.")

        self.playlist = track_names
        self.playlist_index = 0
        self.loop_playlist = loop

        self._play_current(fade_ms)

    def _play_current(self, fade_ms):
        if not self.playlist:
            return

        track_name = self.playlist[self.playlist_index]
        pygame.mixer.music.fadeout(fade_ms)
        pygame.mixer.music.load(self.ost[track_name])
        pygame.mixer.music.play(0, fade_ms=fade_ms)
        self.current_track = track_name

    def next_track(self, fade_ms=FADE_MS):
        if not self.playlist:
            return

        self.playlist_index += 1

        if self.playlist_index >= len(self.playlist):
            if self.loop_playlist:
                self.playlist_index = 0
            else:
                self.playlist = []
                self.current_track = None
                return

        self._play_current(fade_ms)

def adjust_setting(game, index, decrease=False):
    setting = SETTINGS_DEFINITION[index]

    if setting.get("type") != "slider":
        return

    target = _get_setting_target(game, setting)
    key = setting["key"]

    step = setting.get("step", 0.1)
    min_val = setting.get("min", 0.0)
    max_val = setting.get("max", 1.0)

    current_value = getattr(target, key)

    if decrease:
        new_value = max(min_val, current_value - step)
    else:
        new_value = min(max_val, current_value + step)

    setattr(target, key, new_value)

    if setting["target"] == "mixer":
        from scripts.system.soundlib import apply_volume
        apply_volume(game)

    save_config(game)
