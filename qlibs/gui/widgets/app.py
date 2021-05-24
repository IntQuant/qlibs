from .controller import WindowWidgetController
from .render import DefaultRenderer
from ..window import Window
from .behaviors import *

class App:
    def __init__(self, node=None, win=None, ctrl=None, **kwargs):
        self.win = win or Window(**kwargs)
        self.win.make_context_current()
        self.ctrl = ctrl or WindowWidgetController()
        self.root_node = RootNodeB()
        self.ctrl.set_window_node(self.win, self.root_node)
        self.ctrl.assign_to_window(self.win)
        self.rend = DefaultRenderer(window=self.win, is_selected_cb=self.ctrl.is_node_selected)
        if node is not None:
            self.set_node(node)
        self.enabled = True
    
    def render(self, wait_time=None, do_clear=True):
        if self.win.width != 0 and self.win.height != 0:
            if do_clear:
                self.win.ctx.clear(0, 0, 0, 0)
            self.win.make_context_current()
            self.ctrl.make_current()
            self.root_node.make_current()
            self.root_node.recalc_if_needed()
            self.rend.render(self.root_node)
            self.win.swap()
        root_wait_time = self.root_node.requested_update
        if root_wait_time is not None:
            if wait_time is None:
                wait_time = root_wait_time
            else:
                if wait_time > root_wait_time:
                    wait_time = root_wait_time
        if wait_time is not None and wait_time <= 0:
            self.win.poll_events()
        else:
            self.win.wait_events(wait_time)

    def set_node(self, node, layer="main", **kwargs):
        self.root_node.set_layer_node(node, layer, **kwargs)
        
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