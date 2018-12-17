from ..constants import *
from ..helper import *
from ..enums import *

from .GuiNode import *

class GuiNodeHighlighted(GuiNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.highlighted = False

    def highlight(self):
        if not self.highlighted:
            self.highlighted = True
            if self.border is not None:
                self.border.colors = BORDER_HIGHLIGHT_COLOR * 4

    def unlight(self):
        if self.highlighted:
            self.highlighted = False
            if self.border is not None:
                self.border.colors = BORDER_COLOR * 4


class GuiNodeHighlightedByHover(GuiNodeHighlighted):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dispatch_to_all(self, event, args):
        if self.highlighted and (event is EventTypes.PRE_DRAW):
            if not self.contains(*self.window.mouse_pos):
                self.unlight()

    def dispatch_hover(self, x, y):
        super().dispatch_hover(x, y)
        self.highlight()

