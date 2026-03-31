import pygame

sounds = []

def load_sounds():
    sounds.append(pygame.mixer.Sound("../fx/fire.ogg"))
    sounds.append(pygame.mixer.Sound("../fx/explosion.ogg"))
    sounds.append(pygame.mixer.Sound("../fx/game-over.ogg"))
    return sounds

def load_ost():
    return pygame.mixer.music.load("../fx/theme.ogg")