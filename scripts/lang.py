import json

from scripts.utils import resource_path


class Localization:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        self.load(lang)

    def load(self, lang):
        path = resource_path(f"lang/{lang}.json")

        with open(path, "r", encoding="utf-8") as f:
            self.translations = json.load(f)

        self.lang = lang

    def set_language(self, lang):
        self.load(lang)

    def t(self, key, **kwargs):
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        else:
            return text

LANGS = {
    "en": "English",
    "es": "Español"
}

LANG_ORDER = ["en", "es"]
local = Localization('en')

def set_language(game, lang):
    game.state.current_lang = lang
    local.set_language(lang)

def rotate_language(game):
    idx = LANG_ORDER.index(game.state.current_lang)
    idx = (idx + 1) % len(LANG_ORDER)

    new_lang = LANG_ORDER[idx]
    set_language(game, new_lang)
    game.save_config()