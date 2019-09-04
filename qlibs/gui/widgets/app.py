from .controller import WindowWidgetController
from .render import DefaultRenderer
from ..window import Window

class App:
    def __init__(self, node, **kwargs):
        self.win = Window(**kwargs)
        self.ctrl = WindowWidgetController()
        self.ctrl.set_window_node(self.win, node)
        self.ctrl.assign_to_window(self.win)
        self.rend = DefaultRenderer(self.win, node)
        self.node = node
    
    def render(self, wait_time=None):
        self.win.ctx.clear(0, 0, 0, 0)
        self.rend.render()
        self.win.swap()
        self.win.wait_events(wait_time)

    @property
    def should_close(self):
        return self.win.should_close