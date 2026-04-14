from ursina import *
from app.game import Game

if __name__ == "__main__":
    app = Ursina()
    window.color = color.black
    camera.clear_color = color.black
    game = Game()
    def update():
        game.update()
    app.run()