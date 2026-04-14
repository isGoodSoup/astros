class Menu:
    def __init__(self, context, engine):
        self.context = context
        self.engine = engine

        self.transitioning = False
        self.skip = False

    def run(self):
        while self.engine.is_running():
            events = self.engine.poll_events()

            for event in events:
                if event.type == pygame.QUIT:
                    self.engine.stop()

                if event.type == pygame.KEYDOWN:
                    self.transitioning = True

            self.engine.begin_frame()

            self.draw()

            self.engine.end_frame()

            if self.transitioning:
                return self.init_game()
        return None

    def draw(self):
        self.engine.clear()
        self.engine.draw_text("Astros", (100, 100), (255, 255, 255))
        self.engine.draw_text("Press any key", (100, 200), (255, 255, 255))

    def init_game(self):
        from scripts.game import Game
        return Game(self.context)