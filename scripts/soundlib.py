import pygame

sounds = []

def load_sounds():
    sounds.append(pygame.mixer.Sound("assets/fx/fire.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/explosion.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/upgrade.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/levelup.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/fire2.ogg"))
    sounds.append(pygame.mixer.Sound("assets/fx/game-over.ogg"))
    return sounds

def load_ost():
    return pygame.mixer.music.load("assets/fx/theme.ogg")