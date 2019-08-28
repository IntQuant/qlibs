from ...math import IVec, MVec
from itertools import zip_longest
#TODO: handle negative size

try:
    import glfw
    clipboard_get = lambda : glfw.get_clipboard_string(None).decode("utf-8")
    clipboard_set = lambda x: glfw.set_clipboard_string(None, x)
except ImportError:
    #TODO add proper warning
    print(__file__, "Could not import glfw, some functions are unavailable")
    clipboard_get = lambda : None
    clipboard_set = lambda x: None

class NodeB:
    """
    Basic node behavior, does not do any effort to position it's children
    Rendering is separate from behaviors, which only handle events(including resizing)
    """
    type = "node"
    selectable = False
    def __init__(self):
        if not hasattr(self, "_position"):
            self._position = IVec(0, 0)
        if not hasattr(self, "_size"):
            self._size = IVec(100, 100)
        if not hasattr(self, "size_hint"):
            self.size_hint = (None, None)
        if not hasattr(self, "children"):
            self.children = []

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, val):
        self._position = IVec(val)

    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, val):
        self._size = IVec(val)

    def recalc_size(self):
        for child in self.children:
            child.recalc_size()
    
    def add_child(self, child):
        self.children.append(child)
        self.recalc_size()
    
    def handle_event(self, event):
        if event.shall_pass:
            for child in self.children:
                child.handle_event(event)


class ButtonB(NodeB):
    type = "button"
    def __init__(self, name, callback, text=None):
        self.callback = callback
        self.pressed = False
        self.name = name
        self.text = text or name
        self.textalign = "center"
        super().__init__()
        
    def handle_event(self, event):
        if event.type == "mouse":
            hovered = (self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y)
            
            if hovered:
                if event.pressed  and not self.pressed:
                    self.pressed = True
            
            if not event.pressed and self.pressed:
                if hovered:
                    self.callback(self.name)
                self.pressed = False

        super().handle_event(event)


class CentererB(NodeB):
    type = "centerer"
    def __init__(self, sep_x, sep_y, child=None):
        super().__init__()
        self.sep_x = sep_x
        self.sep_y = sep_y
        if child is not None:
            self.add_child(child)
    
    def recalc_size(self):
        tpos = (self.position.x + self.sep_x, self.position.y + self.sep_y)
        tsize = (self.size.x - self.sep_x*2, self.size.y - self.sep_y*2)
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
        

    def add_child(self, child, size_hint=None):
        self.children.append(child)
        self.size_hints.append(size_hint)

    def recalc_size(self):
        n = len(self.children)
        used = 0

        for hint in self.size_hints:
            if hint is not None:
                n -= 1
                used += hint
        if n == 0:
            n = 1

        if self.vertical:
            fr = min(self.max_size, (1-used)/n)
            size =self.size.x-self.spc, (self.size.y*fr)-self.spc
            advancement_index = 1
        else:
            fr = min(self.max_size, (1-used)/n)
            size = self.size.x*fr-self.spc, (self.size.y)-self.spc
            advancement_index = 0
        
        pos = MVec(self.position)
        
        for hint, child in zip_longest(self.size_hints, self.children):            
            if hint is not None:
                if self.vertical:
                    usize = size[0], self.size.y * hint
                else:
                    usize = self.size.x * hint, size[1]
            else:
                usize = size
            child.position = pos + MVec(self.spc, self.spc)
            child.size = usize
            pos[advancement_index] += usize[advancement_index] + self.spc
        super().recalc_size()


class ColumnPlacerB(RCPlacerB):
    type = "columnplacer"
    def __init__(self, spacing=2):
        super().__init__(spacing, vertical=True)


class RowPlacerB(RCPlacerB):
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
        
    def handle_event(self, event):
        if event.type == "key":
            key = event.key
            self.text = self.text[:self.cursor] + key + self.text[self.cursor:]
            self.cursor += 1
        if event.type == "speckey":
            if event.key == "backspace":
                if self.cursor > 0:
                    self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
                    self.cursor -= 1
                if self.cursor < 0:
                    self.cursor = 0
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
    type = "togglebutton"
    def __init__(self, name, callback, text=None):
        self.callback = callback
        self.pressed = False
        self.state = False
        self.name = name
        self.text = text or name
        super().__init__()
        
    def handle_event(self, event):
        if event.type == "mouse":
            if (event.pressed 
            and self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y
            ):
                if not self.pressed:
                    self.state = not self.state
                    self.callback(self.name, self.state)
                    self.pressed = True
            if not event.pressed:
                self.pressed = False

        super().handle_event(event)


class ProgressBarB(NodeB):
    type = "progressbar"
    def __init__(self):
        self.fraction = 0
        super().__init__()


class ScrollableListB(NodeB):
    type = "scrollablelist"
    def __init__(self, shown_items=10):
        super().__init__()
        self.full_list = []
        self.cursor = 0
        self.shown_items = shown_items
        self.placer = ColumnPlacerB()
        self.placer.max_size = 1 / self.shown_items
        self.children.append(self.placer)
    
    def add_child(self, child):
        self.full_list.append(child)
        self.update_view()
    
    def update_view(self):
        self.placer.children = self.full_list[self.cursor:self.cursor+self.shown_items]
        self.recalc_size()

    def handle_event(self, event):
        if event.type == "mouse":
            if (self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y):
                
                if event.scroll_up:
                    if self.cursor > 0:
                        self.cursor -= 1
                        self.update_view()
                if event.scroll_down:
                    if self.cursor < len(self.full_list):
                        self.cursor += 1
                        self.update_view()

        super().handle_event(event)
    
    def recalc_size(self):
        for child in self.children:
            child.size = self.size
            child.position = self.position
            child.recalc_size()