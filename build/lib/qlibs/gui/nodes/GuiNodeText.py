from ..constants import *
from ..helper import *
from ..enums import *

from .GuiNode import *
from .GuiNodeHighlighted import *
from .GuiNodeButton import *

import pyglet

class GuiNodeTextLabelBehavior():
    def __init__(self, *args, **kwargs):
        self.document = pyglet.text.document.UnformattedDocument(
            kwargs["label_text"]) if "label_text" in kwargs else pyglet.text.document.UnformattedDocument("")
        self.document.set_style(0, len(self.document.text), dict(
            color=(255, 255, 255, 255), align="center"))
        self.layout = pyglet.text.layout.TextLayout(
            self.document, self.w, self.h, multiline=True, batch=self.window.batch)
        self.layout.content_valign = "center"
        self.update_layout()

    def update_size(self):
        print("Size")
        super().update_size()
        if self.layout is not None:
            self.update_layout()

    def update_layout(self):
        self.layout.width = self.w - INC_TEXT_HORIZONTAL_MOD
        self.layout.height = self.h
        self.layout.x = self.x + INC_TEXT_HORIZONTAL_MOD
        self.layout.y = self.y


class GuiNodeTextButton(GuiNodeButton, GuiNodeTextLabelBehavior):
    def update_size(self):
        super().update_size()
        if "layout" in self.__dict__ and self.layout is not None:
            super().update_layout()

class GuiNodeTextList(GuiNode):
    def __init__(self, *args, **kwargs):
        """
          Additional keywords:
           document - sets the document to use
           action - action on click
        """
        self.layout = None
        
        super().__init__(*args, **kwargs)
        
        self.action = kwargs["action"]
        self.document = kwargs["document"] if "document" in kwargs else pyglet.text.document.UnformattedDocument("")
        if "document" not in kwargs:
            self.document.set_style(
                0, len(self.document.text), dict(color=(255, 255, 255, 255)))

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, self.w, self.h, multiline=True, batch=self.window.batch)

        self.update_layout()
    
    def dispatch_point_event(self, event_type, x, y, *args):
        if event_type is EventTypes.MOUSE_SCROLL:
            self.layout.view_y += args[1] * SCROLL_SCALE_FACTOR
        elif event_type is EventTypes.MOUSE_PRESS:
            self.action(self.layout.get_line_from_point(x, y))

    def update_size(self):
        super().update_size()
        if self.layout is not None:
            self.update_layout()

    def update_layout(self):
        self.layout.width = self.w - INC_TEXT_HORIZONTAL_MOD
        self.layout.height = self.h
        self.layout.x = self.x + INC_TEXT_HORIZONTAL_MOD
        self.layout.y = self.y

    def delete(self):
        super().delete()
        if self.layout is not None:
            self.layout.delete()
