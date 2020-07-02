from ...math import Vec2
from itertools import zip_longest
import warnings
from .events import GUIEvent
import weakref
#TODO: handle negative size

try:
    import glfw
    def clipboard_get():
        try:
            return glfw.get_clipboard_string(None).decode("utf-8")
        except glfw.GLFWError:
            return ""
    #clipboard_get = lambda : glfw.get_clipboard_string(None).decode("utf-8")
    clipboard_set = lambda x: glfw.set_clipboard_string(None, x)
except ImportError:
    warnings.warn("Could not import glfw, clipboard support is not unavailable")
    clipboard_get = lambda : None
    clipboard_set = lambda x: None

#TODO
#__all__ = ["hint_func_rel", "NodeB", "ButtonB", "CentererB", "ColumnPlacerB", "CustomRenderB", "ProgressBarB", "RadioButtonB", "RadioButtonGroup"]

def hint_func_rel(placer, hints):
    if placer.vertical:
        adv = 0
    else:
        adv = 1
    return [placer.size[adv]/max(placer.size[1-adv], 1)*hint if hint is not None else None for hint in hints]

def hint_func_abs(placer, hints):
    if placer.vertical:
        adv = 0
    else:
        adv = 1
    return [hint/placer.size[1-adv] if hint is not None else None for hint in hints]


class NodeB:
    """
    Basic node behavior, does not do any anything to position it's children
    Rendering is separate from behaviors, which only handles events(including resizing)
    """
    type = "node"
    selectable = False
    def __init__(self, name=None):
        if not hasattr(self, "name"):
            self.name = name
        if not hasattr(self, "_position"):
            self._position = Vec2(0, 0)
        if not hasattr(self, "_size"):
            self._size = Vec2(100, 100)
        if not hasattr(self, "size_hint"):
            self.size_hint = (None, None)
        if not hasattr(self, "children"):
            self.children = []
        self.image_id = None
        self.image_mode = None #Other options are: "fit", "fill"
        self.image_ratio = 1
        self.hidden = False

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, val):
        self._position = Vec2(*val)

    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, val):
        self._size = Vec2(*val)

    def recalc_size(self):
        for child in self.children:
            child.recalc_size()
    
    def add_child(self, child: "NodeB"):
        self.children.append(child)
        self.recalc_size()
    
    def handle_event(self, event: GUIEvent):
        if event.shall_pass:
            for child in self.children:
                child.handle_event(event)
    
    def get_node_by_name(self, name: str):
        for chld in self.children:
            if chld.name == name:
                return chld
        for chld in self.children:
            v = chld.get_node_by_name(name)
            if v is not None:
                return v
        return None
    
    def __getitem__(self, key):
        if not hasattr(self, "_storage"):
            self._storage = weakref.WeakValueDictionary()
        v = self._storage.get(key, None)
        if v is None:
            v = self.get_node_by_name(key)
            if v is not None:
                self._storage[key] = v
        if v is None:
            raise KeyError(f"Node not found: {key}")
        return v

class ButtonB(NodeB):
    """
      Basic button. Callback will be called with button's name as parameter. **text** is displayed text
    """
    type = "button"
    def __init__(self, name: str, callback, text=None):
        super().__init__()
        self.callback = callback
        self.pressed = False
        self.name = name
        self.text = text or name
        self.textalign = "center"
        self.hovered = False
        
    def handle_event(self, event: GUIEvent):
        if event.type == "mouse":
            self.hovered = (self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y)
            
            if self.hovered:
                event.used = True
                if event.pressed  and not self.pressed:
                    self.pressed = True
            else:
                self.pressed = False
            
            if not event.pressed and self.pressed:
                if self.hovered:
                    self.callback(self.name)
                self.pressed = False

        super().handle_event(event)


class CentererB(NodeB):
    """
      Makes it's children smaller by **sep_x** and **sep_y** from each side
    """
    type = "centerer"
    def __init__(self, sep_x, sep_y, child=None):
        super().__init__()
        self.sep_x = sep_x
        self.sep_y = sep_y
        if child is not None:
            self.add_child(child)
    
    def recalc_size(self):
        tpos = (self.position.x + self.sep_x, self.position.y + self.sep_y)
        tsize = (max(self.size.x - self.sep_x*2, 0), max(self.size.y - self.sep_y*2, 0))
        for child in self.children:
            child.position = tpos
            child.size = tsize
        super().recalc_size()


class SizeLimitB(NodeB):
    """
      Limits size of it's children
    """
    type = "centerer"
    def __init__(self, targ_x, targ_y, child=None):
        super().__init__()
        self.targ_x = targ_x
        self.targ_y = targ_y
        if child is not None:
            self.add_child(child)
    
    def recalc_size(self):
        center_x = self.position.x + self.size.x / 2
        center_y = self.position.y + self.size.y / 2

        tx, ty = min(self.targ_x, self.size.x) / 2, min(self.targ_y, self.size.y) / 2
        tpos = center_x - tx, center_y - ty
        tsize = tx*2, ty*2
        for child in self.children:
            child.position = tpos
            child.size = tsize
        super().recalc_size()


class RCPlacerB(NodeB):
    type = "rcplacer"
    def __init__(self, spacing=2, vertical=True, max_size=1):
        super().__init__()
        self.spc = spacing
        self.vertical = vertical
        self.size_hints = list()
        self.max_size = max_size
        self.size_hint_func = None

    def add_child(self, child, size_hint=None):
        self.children.append(child)
        self.size_hints.append(size_hint)

    def recalc_size(self):
        n = len(self.children)
        used = 0
        size_adjust = self.spc*2 * n

        if self.size_hint_func is None:
            size_hints = self.size_hints
        else:
            size_hints = self.size_hint_func(self, self.size_hints)
            #[self.size_hint_func(hint) if hint is not None else None for hint in self.size_hints]

        for hint in size_hints:
            if hint is not None:
                n -= 1
                used += hint
        if n == 0:
            n = 1

        if self.vertical:
            fr = min(self.max_size, (1-used)/n)
            size = self.size.x, (self.size.y*fr)
            advancement_index = 1
        else:
            fr = min(self.max_size, (1-used)/n)
            size = self.size.x*fr, (self.size.y)
            advancement_index = 0
        
        pos = Vec2(*self.position)

        for hint, child in zip_longest(size_hints, self.children):            
            if hint is not None:
                if self.vertical:
                    usize = size[0], self.size.y * hint
                else:
                    usize = self.size.x * hint, size[1]
            else:
                usize = size
            child.position = pos + Vec2(self.spc, self.spc)
            child.size = (usize[0] - self.spc*2, usize[1] - self.spc*2)
            pos[advancement_index] += usize[advancement_index]
        super().recalc_size()


class ColumnPlacerB(RCPlacerB):
    """
      Places children vertically
    """
    type = "columnplacer"
    def __init__(self, spacing=2):
        super().__init__(spacing, vertical=True)


class RowPlacerB(RCPlacerB):
    """
      Places children horizontally
    """
    type = "rowplacer"
    def __init__(self, spacing=2):
        super().__init__(spacing, vertical=False)


class TextInputB(NodeB):
    type = "textinput"
    selectable = True
    def __init__(self, text="", name="default", callback=None):
        super().__init__()
        self.text = text
        self.callback = callback
        self.cursor = 0
        self.textalign = "left"
        self.name = name
        
    def handle_event(self, event: GUIEvent):
        if event.type == "key":
            key = event.key
            self.text = self.text[:self.cursor] + key + self.text[self.cursor:]
            self.cursor += 1
        if event.type == "speckey":
            if event.key == "backspace":
                if self.cursor > 0:
                    self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
                    self.cursor -= 1
            elif event.key == "delete":
                if self.cursor < len(self.text):
                    self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
            elif event.key == "enter":
                if self.callback:
                    self.callback(self.text)
            elif event.key == "left":
                self.cursor -= 1
                if self.cursor < 0:
                    self.cursor = 0
            elif event.key == "right":
                self.cursor += 1
                if self.cursor > len(self.text):
                    self.cursor = len(self.text)
            
            elif event.mods.ctrl and event.key == "v":
                clipboard = clipboard_get()
                self.text += self.text[:self.cursor] + clipboard + self.text[self.cursor:]
                self.cursor += len(clipboard)
            elif event.mods.ctrl and event.key == "c":
                clipboard_set(self.text)
            elif event.mods.ctrl and event.key == "x":
                clipboard_set(self.text)
                self.text = ""


class ToggleButtonB(NodeB):
    """
      Just like button, but toggleable. Callback also recieves **self.state**, which is True is button is active
    """
    type = "togglebutton"
    def __init__(self, name, callback, text=None):
        super().__init__()
        self.callback = callback
        self.pressed = False
        self.state = False
        self.name = name
        self.text = text or name
        self.hover = False
        
    def handle_event(self, event: GUIEvent):
        if event.type == "mouse":
            self.hovered = (
                self.position.x <= event.pos.x <= self.position.x + self.size.x 
                and self.position.y <= event.pos.y <= self.position.y + self.size.y
            )
            if self.hovered:
                event.used = True
            if event.pressed and self.hovered:
                if not self.pressed:
                    self.state = not self.state
                    self.callback(self.name, self.state)
                    self.pressed = True
            if not event.pressed:
                self.pressed = False

        super().handle_event(event)


class ProgressBarB(NodeB):
    """
      Progress bar. **self.fraction** is how full it is, with value from 0 to 1 inclusively.
    """
    type = "progressbar"
    def __init__(self):
        super().__init__()
        self.fraction = 0


class ScrollableListB(NodeB):
    """
      List which can be scrolled
    """
    type = "scrollablelist"
    def __init__(self, shown_items=10):
        super().__init__()
        self.full_list = []
        self.cursor = 0
        self.shown_items = shown_items
        self.placer = ColumnPlacerB()
        self.placer.max_size = 1 / self.shown_items
        self.children.append(self.placer)
        self.scrollbar_size = 10
        self.scrollbar = ScrollBarB(cb=self.scrollbar_cb)
        self.children.append(self.scrollbar)
        
    def scrollbar_cb(self, pos):
        self.cursor = round(len(self.full_list)*pos)
        self.update_view()

    def add_child(self, child):
        self.full_list.append(child)
        self.update_view()
    
    def update_view(self):
        self.placer.children = self.full_list[self.cursor:self.cursor+self.shown_items]
        self.recalc_size()

    def handle_event(self, event: GUIEvent):
        if event.type == "mouse":
            if (self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y):
                event.used = True
                if event.scroll_up:
                    if self.cursor > 0:
                        self.cursor -= 1
                        self.scrollbar.pos = self.cursor / len(self.full_list)
                        self.update_view()
                if event.scroll_down:
                    if self.cursor < len(self.full_list):
                        self.cursor += 1
                        self.scrollbar.pos = self.cursor / len(self.full_list)
                        self.update_view()

        super().handle_event(event)
    
    def recalc_size(self):
        self.placer.size = self.size.x-self.scrollbar_size, self.size.y
        self.placer.position = self.position
        self.placer.recalc_size()
        self.scrollbar.position = self.placer.position.x + self.placer.size.x, self.placer.position.y
        self.scrollbar.size = (self.scrollbar_size, self.size.y)
        self.scrollbar.recalc_size()


class ScrollableStringListB(ScrollableListB):
    """
      Scrollable list of strings. Has **full_list** property which contains used list.
      Callback should be a function with one argument - index of clicked string.
      **override_node_type** changes type of buttons to node, so that they are renderer like usual NodeB.
      Call `self.update_view()` after changing **self.full_list** to update
    """
    def __init__(self, callback=None, shown_items=10, override_node_type=True):
        super().__init__(shown_items)
        self.callback = callback
        self._override_node_type = override_node_type
    
    def callback_adapter(self, num):
        if self.callback is not None:
            self.callback(self.cursor+num)

    def update_view(self):
        if len(self.placer.children) != self.shown_items:
            self.placer.children = [ButtonB(name=i, callback=self.callback_adapter) for i in range(self.shown_items)]
            if self._override_node_type:
                for child in self.placer.children:
                    child.type = "node"
        
        for child in self.placer.children:
            child.text = ""


        for child, data in zip(self.placer.children, self.full_list[self.cursor:self.cursor+self.shown_items]):
            child.text = data
        self.recalc_size()


class ScrollBarB(NodeB):
    type = "scrollbar"
    def __init__(self, direction="vertical", callback=None, cb=None):
        super().__init__()
        possible = ["vertical", "horizontal"]
        if direction not in possible:
            raise ValueError("Wrong direction value %s, should one of %s" % (direction, possible))
        self.direction = 1 if direction == "vertical" else 0
        self.callback = cb or callback
        if cb is not None:
            warnings.warn("Please use callback instead of cb", DeprecationWarning)
        self.pos = 0
    
    def handle_event(self, event: GUIEvent):
        if event.type == "mouse":
            if (self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y
            ):
                event.used = True
                if event.pressed:
                    ratio = (event.pos[self.direction] - self.position[self.direction]) / self.size[self.direction]
                    self.pos = max(0, min(1, ratio))
                    if self.callback is not None:
                        self.callback(self.pos)


class CustomRenderB(NodeB):
    type = "customrender"
    def __init__(self, render):
        super().__init__()
        self.render = render


class RadioButtonGroup:
    def __init__(self):
        self.selected = None

class RadioButtonB(NodeB):
    type = "radiobutton"
    def __init__(self, group: RadioButtonGroup):
        super().__init__()
        self.group = group
        if group.selected is None:
            group.selected = self
    
    def handle_event(self, event):
        if event.type == "mouse":
            self.hovered = (
                self.position.x <= event.pos.x <= self.position.x + self.size.x 
                and self.position.y <= event.pos.y <= self.position.y + self.size.y
            )
            if self.hovered:
                event.used = True
            if event.pressed and self.hovered:
                if not self.pressed:
                    self.group.selected = self
                    self.pressed = True
            if not event.pressed:
                self.pressed = False

        super().handle_event(event)

        