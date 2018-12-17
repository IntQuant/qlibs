from .GuiNode import *
from .GuiNodeHighlighted import *

import pyglet

class GuiNodeIncrementalText(GuiNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.document = pyglet.text.document.UnformattedDocument(
            kwargs["label_text"]) if "label_text" in kwargs else pyglet.text.document.UnformattedDocument("")
        self.document.set_style(0, len(self.document.text), dict(
            color=(255, 255, 255, 255), align="center"))
        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, self.w, self.h, multiline=True, batch=self.window.batch)
        self.layout.content_valign = "center"
        self.update_layout()
        

    def update_size(self):
        super().update_size()
        if hasattr(self, "layout"):
            self.update_layout()

    def update_layout(self):
        self.layout.width = self.w - INC_TEXT_HORIZONTAL_MOD
        self.layout.height = self.h
        self.layout.x = self.x + INC_TEXT_HORIZONTAL_MOD
        self.layout.y = self.y





class GuiNodeIncrementalTextEditor(GuiNodeHighlighted):
    def __init__(self, *args, **kwargs):
        """
          Additional keywords:
           document - sets the document to use
        """
        self.layout = None

        super().__init__(*args, **kwargs)

        self.document = kwargs["document"] if "document" in kwargs else pyglet.text.document.UnformattedDocument(
            "")
        if "document" not in kwargs:
            self.document.set_style(
                0, len(self.document.text), dict(color=(255, 255, 255, 255)))

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, self.w, self.h, multiline=True, batch=self.window.batch)
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.color = CARET_COLOR
        self.caret.visible = False

        self.update_layout()

    def highlight(self):
        super().highlight()
        self.caret.visible = True

    def unlight(self):
        super().unlight()
        self.caret.visible = False

    def dispatch_to_all(self, event, args):
        if self.highlighted and (event is EventTypes.PRE_DRAW):
            if self.window.node.selected is not self:
                self.unlight()

    def dispatch_click(self, x, y, button, mod):
        super().dispatch_click(x, y, button, mod)
        self.window.node.selected = self
        self.highlight()

    def dispatch_event(self, event, args):
        if self.window.node.selected is self:
            if event is EventTypes.MOUSE_PRESS:
                self.caret.on_mouse_press(*args)
            elif event is EventTypes.MOUSE_DRAG:
                self.caret.on_mouse_drag(*args)
            elif event is EventTypes.TEXT:
                self.caret.on_text(*args)
            elif event is EventTypes.TEXT_MOTION:
                self.caret.on_text_motion(*args)
            elif event is EventTypes.TEXT_MOTION_SELECT:
                self.caret.on_text_motion_select(*args)

    def update_size(self):
        super().update_size()
        if self.layout is not None:
            self.update_layout()

    def update_layout(self):
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout.width = self.w - INC_TEXT_HORIZONTAL_MOD
        self.layout.height = self.h
        self.layout.x = self.x + INC_TEXT_HORIZONTAL_MOD
        self.layout.y = self.y

    def delete(self):
        super().delete()
        if self.layout is not None:
            self.layout.delete()
