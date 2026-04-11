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

current_lang = 0
langs = ['en', 'es']
local = Localization(langs[current_lang])

def rotate_language():
    global current_lang, local
    current_lang = (current_lang + 1) % len(langs)
    local.set_language(langs[current_lang])