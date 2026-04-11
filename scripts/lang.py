import json
import os

class Localization:
    def __init__(self, lang="en"):
        self.lang = lang
        self.translations = {}
        self.load(lang)

    def load(self, lang):
        path = os.path.join("lang", f"{lang}.json")

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

langs = ['en', 'es']
local = Localization(langs[0])