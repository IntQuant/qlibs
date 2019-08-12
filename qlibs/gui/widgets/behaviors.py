from ...math import IVec, MVec
#TODO: handle negative size

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
        #Not sure if this is required
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
        super().__init__()
        
    def handle_event(self, event):
        if event.type == "mouse":
            if (event.pressed 
            and self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y
            ):
                if not self.pressed:
                    self.callback(self.name)
                    self.pressed = True
            if not event.pressed:
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
            

class ColumnPlacerB(NodeB):
    type = "columnplacer"
    def __init__(self, spacing=2):
        super().__init__()
        self.spc = spacing

    def recalc_size(self):
        n = len(self.children)
        #TODO: handle size_hints
        size = self.size.x-self.spc, (self.size.y//n)-self.spc
        pos = MVec(self.position)
        for child in self.children:
            child.position = pos + MVec(self.spc, self.spc)
            child.size = size
            pos.y += size[1]+self.spc
        super().recalc_size()


class TextInputB(NodeB):
    type = "textinput"
    selectable = True
    def __init__(self, text="", name="default"):
        super().__init__()
        self.text = text
        
    def handle_event(self, event):
        if event.type == "key":
            key = event.key
            self.text += key
        if event.type == "speckey":
            if event.key == "backspace":
                self.text = self.text[:-1]


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