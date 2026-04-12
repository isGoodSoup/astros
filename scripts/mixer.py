import pygame
from scripts.settings import FADE_MS
from scripts.soundlib import load_sounds, load_ost


class Mixer:
    def __init__(self):
        self.sounds = load_sounds()
        self.ost = load_ost()
        self.current_track = None

        self.playlist = []
        self.playlist_index = 0
        self.loop_playlist = False

        self.MUSIC_END = pygame.USEREVENT + 2
        pygame.mixer.music.set_endevent(self.MUSIC_END)

    def play_music(self, track_name, loop=True, fade_ms=FADE_MS):
        if self.current_track == track_name:
            return

        if track_name not in self.ost:
            raise ValueError(f"Track '{track_name}' not found in OST.")

        pygame.mixer.music.fadeout(fade_ms)
        pygame.mixer.music.load(self.ost[track_name])
        pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)

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