from abc import ABC, abstractmethod


class Engine(ABC):
    @abstractmethod
    def poll_events(self):
        pass

    @abstractmethod
    def begin_frame(self):
        pass

    @abstractmethod
    def end_frame(self):
        pass

    @abstractmethod
    def draw_text(self, text, pos, color):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def is_running(self):
        pass

    @abstractmethod
    def stop(self):
        pass