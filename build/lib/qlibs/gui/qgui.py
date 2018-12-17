from .constants import *
from .helper import *
from .enums import *

from .nodes.GuiNode import *
from .nodes.GuiNodeHighlighted import *
from .nodes.GuiNodeButton import *
from .nodes.GuiNodeText import *
from .nodes.GuiNodeIncrementalText import *

import pyglet

class MainGuiNode(GuiNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected = None
        self.dispatch_events_to = []
        self.nodes = []

    def dispatch_to_all(self, event, args):
        for node in self.nodes:
            if node.recieves_events:
                node.dispatch_to_all(event, args)

    def dispatch_event(self, event, args):
        if event is EventTypes.MOUSE_MOTION:
            self.dispatch_hover(*args[:2])
        elif event is EventTypes.MOUSE_PRESS:
            self.dispatch_click(*args)
        if self.selected is not None:
            self.selected.dispatch_event(event, args)
        for dispatcher in self.dispatch_events_to:
            if dispatcher.recieves_events:
                dispatcher.dispatch_event(event, args)


class Window(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node = None
        self.additional_draw = None
        self.batch = pyglet.graphics.Batch()
        self.node = MainGuiNode(window=self)
        self.mouse_pos = (0, 0)
        self.win_size = [800, 600]

    def draw_rectangle_outline(self, x1, y1, x2, y2, color):
        return self.batch.add_indexed(4, pyglet.gl.GL_LINES, None,
                                      (0, 1, 1, 2, 2, 3, 3, 0),
                                      # make_rectangle_verticle_sequence could be used
                                      ('v2f', (x1, y1, x2,
                                               y1, x2, y2, x1, y2)),
                                      ('c4f', color*4)
                                      )

    def on_resize(self, x, y):
        super().on_resize(x, y)
        self.win_size[0] = x
        self.win_size[1] = y
        self.node.update_size()

    def on_draw(self):
        self.node.dispatch_to_all(EventTypes.PRE_DRAW, None)
        pyglet.gl.glClearColor(*BG_COLOR)
        self.clear()
        if self.additional_draw is not None:
            self.additional_draw()
        self.batch.draw()
        
        self.node.dispatch_to_all(
            EventTypes.POST_DRAW, None)
    
    def on_mouse_scroll(self, *args):
        self.node.dispatch_point_event(EventTypes.MOUSE_SCROLL, *args)
    
    def on_mouse_motion(self, *args):
        self.node.dispatch_point_event(EventTypes.MOUSE_MOTION, *args)
        self.mouse_pos = args[:2]
        self.node.dispatch_event(
            EventTypes.MOUSE_MOTION, args)

    def on_mouse_press(self, *args):
        self.node.dispatch_point_event(EventTypes.MOUSE_PRESS, *args)
        self.node.dispatch_event(
            EventTypes.MOUSE_PRESS, args)

    def on_mouse_drag(self, *args):
        self.node.dispatch_point_event(EventTypes.MOUSE_DRAG, *args)
        self.node.dispatch_event(
            EventTypes.MOUSE_DRAG, args)

    def on_mouse_release(self, *args):
        self.node.dispatch_point_event(EventTypes.MOUSE_RELEASE, *args)
        self.node.dispatch_event(
            EventTypes.MOUSE_RELEASE, args)

    def on_text(self, *args):
        self.node.dispatch_event(EventTypes.TEXT, args)

    def on_text_motion(self, *args):
        self.node.dispatch_event(
            EventTypes.TEXT_MOTION, args)

    def on_text_motion_select(self, *args):
        self.node.dispatch_event(
            EventTypes.TEXT_MOTION_SELECT, args)


if __name__ == "__main__":
    window = Window(resizable=True)
    print("Created window")
    node = GuiNode(window.node, 1, 0.1, -0.4, 0.4)
    button = GuiNodeTextButton(window.node, 0, 0.75, 0.5, 0.25, action=lambda: print(
        "Pressed"), label_text="Press Me! bla-bla-bla")
    
    d = pyglet.text.document.UnformattedDocument("\n".join((str(i) for i in range(100))))
    d.set_style(0, len(d.text), dict(color=(255, 255, 255, 255)))
    
    text = GuiNodeTextList(window.node, 0.1, 0.5, 0.5, 0.2,
     document=d, action=lambda x: print(x))
    text2 = GuiNodeIncrementalTextEditor(window.node, 0.1, 0, 0.5, 0.2)
    pyglet.clock.schedule_interval(lambda dt: True, 1/20)
    pyglet.app.run()
