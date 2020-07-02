from .controller import WindowWidgetController
from .render import DefaultRenderer
from ..window import Window

class App:
    def __init__(self, node, win=None, **kwargs):
        self.win = win or Window(**kwargs)
        self.ctrl = WindowWidgetController()
        self.ctrl.set_window_node(self.win, node)
        self.ctrl.assign_to_window(self.win)
        self.rend = DefaultRenderer(self.win, node, is_selected_cb=self.ctrl.is_node_selected)
        self.node = node
        self.enabled = True
    
    def render(self, wait_time=None):
        self.win.ctx.clear(0, 0, 0, 0)
        self.rend.render()
        self.win.swap()
        if wait_time <= 0:
            self.win.poll_events()
        else:
            self.win.wait_events(wait_time)

    def set_node(self, node):
        self.node = node
        self.rend.node = node
        self.ctrl.set_window_node(self.win, node)
        
    def disable(self):
        if self.enabled:
            self.enabled = False
            self.ctrl.unassign_from_window(self.win)
    
    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.ctrl.assign_to_window(self.win)

    @property
    def should_close(self):
        return self.win.should_close

    @property
    def ctx(self):
        return self.win.ctx