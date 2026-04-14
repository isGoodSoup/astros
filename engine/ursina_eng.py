from ursina import *

class UrsinaEngine(Entity):
    def __init__(self):
        super().__init__()
        self.running = True

    def clear(self):
        pass

    def poll_events(self):
        return []

    def begin_frame(self):
        pass

    def end_frame(self):
        pass

    def draw_text(self, text, pos, color):
        Text(text=text, position=pos, color=color)

    def is_running(self):
        return self.running

    def stop(self):
        self.running = False