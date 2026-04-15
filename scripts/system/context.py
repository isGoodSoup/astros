from scripts.system.lang import Localization

class AppContext:
    def __init__(self, lang: str = "en"):
        self.local = Localization(lang)