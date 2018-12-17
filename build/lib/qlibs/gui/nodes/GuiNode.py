from ..constants import *
from ..helper import *

class GuiNode():
    def __init__(self, parent=None, rx=0, ry=0, rwidth=1, rheight=1, window=None, **kwargs):
        self.parent = parent
        self.children = []

        self.shown = True
        self.recieves_events = True

        self.window = window

        if rwidth >= 0:
            self.rx = rx
            self.rw = rwidth
        else:
            self.rx = rx + rwidth
            self.rw = -rwidth

        if rheight >= 0:
            self.ry = ry
            self.rh = rheight
        else:
            self.ry = ry + rheight
            self.rh = -rheight

        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.border = None

        self.draw_border = True  # TODO

        if self.parent is not None:
            self.parent.add_child(self)

        if (self.window is not None) and self.window.batch is not None:
            self.update_size()
            if self.window.node is not None:
                self.window.node.nodes.append(self)

        #super().__init__(**kwargs)

    def convert_to_abs(self, rx, ry):
        x = self.x + self.w * rx
        y = self.y + self.h * ry
        return x, y

    def convert_to_abs_hw(self, rx, ry):
        return self.w*rx, self.h*ry

    def update_border(self):
        if self.border is None and self.draw_border:
            print(self.x, self.y, self.w, self.h)
            self.border = self.window.draw_rectangle_outline(
                self.x+1, self.y+1, self.x+self.w, self.y+self.h, BORDER_COLOR)
        else:
            self.border.vertices = make_rectangle_verticle_sequence(
                self.x+1, self.y+1, self.x+self.w, self.y+self.h)

    def update_size(self):
        if self.parent is not None:
            self.x, self.y = self.parent.convert_to_abs(
                self.rx, self.ry)
            self.w, self.h = self.parent.convert_to_abs_hw(
                self.rw, self.rh)
        elif self.window is not None:
            self.x, self.y = 0, 0
            self.w, self.h = self.window.get_size()

        for chld in self.children:
            chld.update_size()

        self.update_border()

    def contains(self, x, y):
        return ((self.x <= x <= self.x + self.w) and
                (self.y <= y <= self.y + self.h))

    def dispatch_to_all(self, event, args):
        pass

    def dispatch_event(self, event, args):
        pass

    def dispatch_click(self, x, y, button, mod):
        for chld in self.children:
            if chld.contains(x, y) and chld.recieves_events:
                chld.dispatch_click(x, y, button, mod)
                if BREAK_ON_NEXT_DISPATCHER_FOUND:
                    break

    def dispatch_hover(self, x, y):
        for chld in self.children:
            if chld.contains(x, y) and chld.recieves_events:
                chld.dispatch_hover(x, y)
                if BREAK_ON_NEXT_DISPATCHER_FOUND:
                    break
    
    def dispatch_point_event(self, event_type, x, y, *args):
        for chld in self.children:
            if chld.contains(x, y) and chld.recieves_events:
                chld.dispatch_point_event(event_type, x, y, *args)
                if BREAK_ON_NEXT_DISPATCHER_FOUND:
                    break

    def add_child(self, obj):
        self.children.append(obj)
        if self.window is not None:
            obj.window = self.window

    def delete(self):
        if self.border is not None:
            self.border.delete()
        if self.window is not None:
            try:
                self.window.node.nodes.remove(self)
            except ValueError:
                pass
        del self.children

    def __del__(self):
        self.delete()

    def hide(self):
        if self.shown:
            self.shown = False
            self.draw_border = False
            if self.window is not None and self.window.node.selected is self:
                self.window.node.selected = None

            if self.border is not None:
                self.border.delete()
                del self.border
        for chld in self.children:
            chld.hide()

        self.recieves_events = True

    def show(self):
        if not self.shown:
            self.shown = True
            self.draw_border = True
            self.update_border()

        for chld in self.children:
            chld.show()

        self.recieves_events = False
