from .GuiNodeHighlighted import *

class GuiNodeButton(GuiNodeHighlightedByHover):
    def __init__(self, *args, **kwargs):
        """Has 'action' keyword - sets up button callback"""
        super().__init__(*args, **kwargs)
        self.action = kwargs["action"] if "action" in kwargs else None

    def dispatch_click(self, x, y, button, mod):
        super().dispatch_click(x, y, button, mod)
        if self.action is not None:
            self.action()
