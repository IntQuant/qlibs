from contextvars import ContextVar
from typing import Union
from ...math import Vec2
from itertools import zip_longest
import warnings
from .events import GUIEvent
import weakref
from collections import defaultdict

from enum import Enum
from dataclasses import dataclass
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
__all__ = [
    "ButtonB",
    "CentererB",
    "ColumnPlacerB",
    "CustomRenderB",
    "NodeB",
    "ProgressBarB",
    "RadioButtonB",
    "RadioButtonGroup",
    "RCPlacerB",
    "RowPlacerB",
    "ScrollableListB",
    "ScrollableStringListB",
    "ScrollBarB",
    "SizeLimitB",
    "TextInputB",
    "TextNodeB",
    "ToggleButtonB",
    "WindowNodeB",
    "RootNodeB",
    "ColumnDiagramB",
    "DiagramDatum",
    "QlibsNodeTypes",
    "hint_func_rel",
    "hint_func_abs",
    "current_root_node",
]

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
    if placer.size[1-adv] == 0:
        return hints
    return [hint/placer.size[1-adv] if hint is not None else None for hint in hints]

class QlibsNodeTypes(Enum):
    COLUMN_DIAGRAM = "column_diagram"


class NodeB:
    """
    Basic node behavior, does not do any anything to position it's children
    Rendering is separate from behaviors, which only handles events(including resizing)
    """
    type = "node"
    selectable = False
    def __init__(self, name=None, text=None):
        if not hasattr(self, "name"):
            self.name = name
        if not hasattr(self, "_position"):
            self._position = Vec2(0, 0)
        if not hasattr(self, "_size"):
            self._size = Vec2(100, 100)
        if not hasattr(self, "size_hint"):
            self.size_hint = (None, None)
        if not hasattr(self, "children") and type(self) != RootNodeB:
            self.children = []
        self.image_id = None
        self.image_mode = None #Other options are: "fit", "fill"
        self.image_ratio = 1
        self.hidden = False
        if text is not None:
            self.__text = text
        else:
            self.__text = ""
    
    @property
    def text(self):
        return self.__text
    
    @text.setter
    def text(self, value):
        self.__text = value

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

class TextNodeB(NodeB):
    type="text"
    def __init__(self, text, *, scale=32, name=None):
        super().__init__()
        self.name = name
        self.text = text
        self.scale = scale


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
    def __init__(self, sep_x, sep_y, child=None, **kwargs):
        super().__init__(**kwargs)
        self.sep_x = sep_x
        self.sep_y = sep_y
        if child is not None:
            self.add_child(child)
    
    @property
    def child(self):
        return self.children[0]
    
    @child.setter
    def child(self, val):
        if self.children:
            self.children[0] = val
        else:
            self.children.append(val)
        self.recalc_size()

    def recalc_size(self):
        tpos = (self.position.x + self.sep_x, self.position.y + self.sep_y)
        tsize = (max(self.size.x - self.sep_x*2, 0), max(self.size.y - self.sep_y*2, 0))
        for child in self.children:
            child.position = tpos
            child.size = tsize
        super().recalc_size()


class SizeLimitB(NodeB):
    """
      Limits size of it's children.
    """
    type = "centerer"
    def __init__(self, targ_x, targ_y, child=None, **kwargs):
        super().__init__(**kwargs)
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
    """
      Places it's children either horizontally or vertically, with size_hint controlling their (relative) size.
    """
    type = "rcplacer"
    def __init__(self, spacing=0, vertical=True, max_size=1, size_hint_func=None, **kwargs):
        super().__init__(**kwargs)
        self.spc = spacing
        self.vertical = vertical
        self.size_hints = list()
        self.max_size = max_size
        self.size_hint_func = size_hint_func

    def add_child(self, child, size_hint=None):
        self.children.append(child)
        self.size_hints.append(size_hint)
        self.recalc_size()

    def recalc_size(self):
        n = len(self.children)
        used = 0
        size_adjust = self.spc*2

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
      Places children vertically.
      See RCPlacerB for more.
    """
    type = "columnplacer"
    def __init__(self, spacing=0, **kwargs):
        super().__init__(spacing, vertical=True, **kwargs)


class RowPlacerB(RCPlacerB):
    """
      Places children horizontally.
      See RCPlacerB for more.
    """
    type = "rowplacer"
    def __init__(self, spacing=0, **kwargs):
        super().__init__(spacing, vertical=False, **kwargs)


class TextInputB(NodeB):
    """
      Allows to edit it's *text*. 
      *callback* is called on enter and gets current text as an argument.
    """
    type = "textinput"
    selectable = True
    def __init__(self, text="", name="default", callback=None, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self.callback = callback
        self.cursor = len(text)
        self.textalign = "left"
        self.name = name

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        if len(self._text) < self.cursor:
            self.cursor = len(self._text)
        if self.cursor < 0:
            self.cursor = 0
        
    def handle_event(self, event: GUIEvent):
        if event.type == "key":
            key = event.key
            self.text = self.text[:self.cursor] + key + self.text[self.cursor:]
            self.cursor += 1
        if event.type == "speckey":
            if event.key == "backspace":
                if self.cursor > 0:
                    self.cursor -= 1
                    self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
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
    def __init__(self, name, callback, text=None, state=False, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.pressed = False
        self.state = state
        self.name = name
        self.text = text or name
        self.hovered = False
        
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
    def __init__(self, name=None, **kwargs):
        super().__init__(**kwargs)
        self.fraction = 0
        self.name = name


class ScrollableListB(NodeB):
    """
      List which can be scrolled.
      If *target_size* is not None(default), amount of shown items will be adjusted automatically.
    """
    type = "scrollablelist"
    def __init__(self, shown_items=10, target_size=50, **kwargs):
        super().__init__(**kwargs)
        self.full_list = []
        self.cursor = 0
        self.shown_items = shown_items
        self.placer = ColumnPlacerB()
        self.placer.max_size = 1 / self.shown_items
        self.children.append(self.placer)
        self.scrollbar_size = 10
        self.scrollbar = ScrollBarB(callback=self.scrollbar_cb)
        self.children.append(self.scrollbar)
        self.target_size = target_size
        #self.update_view()
        
    def scrollbar_cb(self, pos):
        self.cursor = round((len(self.full_list)-1)*pos)
        self.update_view()

    def add_child(self, child):
        self.full_list.append(child)
        self.update_view()
    
    def update_view(self):
        self.placer.max_size = 1 / self.shown_items
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
                        self.scrollbar.pos = self.cursor / (len(self.full_list)-1)
                        self.update_view()
                if event.scroll_down:
                    if self.cursor < len(self.full_list)-1:
                        self.cursor += 1
                        self.scrollbar.pos = self.cursor / (len(self.full_list)-1)
                        self.update_view()

        super().handle_event(event)
    
    def recalc_size(self):
        if self.target_size is not None:
            v = max(1, int(self.size.y // self.target_size))
            if v != self.shown_items:
                self.shown_items = v
                self.update_view()
        self.placer.size = self.size.x-self.scrollbar_size, self.size.y
        self.placer.position = self.position
        self.placer.recalc_size()
        self.scrollbar.position = self.placer.position.x + self.placer.size.x, self.placer.position.y + self.placer.spc
        self.scrollbar.size = (self.scrollbar_size, self.size.y - self.placer.spc*2)
        self.scrollbar.recalc_size()


class ScrollableStringListB(ScrollableListB):
    """
      Scrollable list of strings. Has **full_list** property which contains used list.
      Callback should be a function with one argument - index of clicked string.
      **override_node_type** changes type of buttons to node, so that they are renderer like usual NodeB.
      Call `self.update_view()` after changing **self.full_list** to update.
      If *target_size* is not None(default), amount of shown items will be adjusted automatically.
    """
    def __init__(self, callback=None, shown_items=10, target_size=50, override_node_type=True, name=None, **kwargs):
        super().__init__(shown_items, **kwargs)
        self.callback = callback
        self._override_node_type = override_node_type
        self.name = name
        self.target_size = target_size
    
    def callback_adapter(self, num):
        if self.callback is not None:
            self.callback(self.cursor+num)

    def update_view(self):
        self.placer.max_size = 1 / self.shown_items
        if len(self.placer.children) != self.shown_items:
            self.placer.children = [ButtonB(name=i, callback=self.callback_adapter) for i in range(self.shown_items)]
            #if self._override_node_type:
            #    for child in self.placer.children:
            #        child.type = "node"
        
        for child in self.placer.children:
            child.text = ""


        for child, data in zip(self.placer.children, self.full_list[self.cursor:self.cursor+self.shown_items]):
            child.text = data
        self.recalc_size()


class ScrollBarB(NodeB):
    """
      ScrollBar.
      *direction* can be one of ["vertical", "horizontal"].
      *callback* is called when updated, with **self.pos** as an argument.
      **self.pos** is a position (ranges from 0 to 1 inclusive).
    """
    type = "scrollbar"
    def __init__(self, direction="vertical", callback=None, cb=None, **kwargs):
        super().__init__(**kwargs)
        possible = ["vertical", "horizontal"]
        if direction not in possible:
            raise ValueError("Wrong direction value %s, should one of %s" % (direction, possible))
        self.direction = 1 if direction == "vertical" else 0
        self.callback = cb or callback
        if cb is not None:
            warnings.warn("Please use callback instead of cb", DeprecationWarning)
        self.pos = 0
        self._is_dragged = False
    
    def handle_event(self, event: GUIEvent):
        if event.type == "mouse":
            if (self.position.x <= event.pos.x <= self.position.x + self.size.x 
            and self.position.y <= event.pos.y <= self.position.y + self.size.y
            ) or self._is_dragged:
                if event.pressed:
                    event.used = True
                    ratio = (event.pos[self.direction] - self.position[self.direction]) / self.size[self.direction]
                    self.pos = max(0, min(1, ratio))
                    if self.callback is not None:
                        self.callback(self.pos)
                    self._is_dragged = True
                else:
                    self._is_dragged = False


class CustomRenderB(NodeB):
    """
      *render* is a callback. This will be called by rendering, with viewport set to node's position and size. Recieves this node as an argument.
    """
    type = "customrender"
    def __init__(self, render, **kwargs):
        super().__init__(**kwargs)
        self.render = render


class RadioButtonGroup:
    """
      Group of buttons.
    """
    def __init__(self):
        self.selected = None


class RadioButtonB(NodeB):
    """
      Just like ToggleButtonB, but only one button from the group can be active at once.
    """
    type = "radiobutton"
    def __init__(self, group: RadioButtonGroup, **kwargs):
        super().__init__(**kwargs)
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


@dataclass
class DiagramDatum:
    value: float
    tag: Union[str, None] = None


class ColumnDiagramB(NodeB):
    type = QlibsNodeTypes.COLUMN_DIAGRAM
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.displayed_data = []


class WindowNodeB(NodeB):
    type = "window"
    def __init__(self, closeable=False, **kwargs):
        super().__init__(**kwargs)
        self._dragged = False
        self._last_mouse_pos = Vec2(0, 0)
        self.ext_extra_priority = 0
        self._docked = False
        self.size = (300, 300)
        self.min_size = Vec2(100, 100)
        self.closeable = closeable
        self.recalc_size()
    
    def set_child(self, node):
        self.children = [node]
        root = current_root_node.get(None)
        if root is not None:
            root.requires_size_recalculation = True
    
    def set_node(self, node):
        self.set_child(node)

    @property
    def ext_docked(self):
        return self._docked

    @ext_docked.setter
    def ext_docked(self, value):
        if value != self._docked:
            self._docked = value
            root = current_root_node.get(None)
            if root is not None:
                root.requires_size_recalculation = True

    def ext_set_focus(self, focus):
        self.ext_extra_priority = 1 if focus else 0

    def recalc_size(self):
        spcy = 20
        spcb = 10
        self.content_pos = self.position + Vec2(4, spcy)
        self.content_size = self.size - Vec2(8, spcy+spcb)
        self.header_size = Vec2(self.size.x, spcy-2)
        for chld in self.children:
            chld.position = self.content_pos
            chld.size = self.content_size
        super().recalc_size()
    
    def close(self):
        current_root_node.get().del_node(self)

    def handle_event(self, event: GUIEvent):
        pass_event = True
        if event.type == "mouse":
            inside = event.pos.in_box(self.position, self.position+self.size)
            if event.pressed:
                self.ext_set_focus(inside or self._dragged)
            if inside:
                event.used = True
            controls_me = inside and not event.pos.in_box(self.content_pos, self.content_pos+self.content_size)
            if controls_me:
                if 1 in event.pressed_buttons and self.closeable:
                    self.close()
                if 2 in event.pressed_buttons:
                    self.ext_docked = not self.ext_docked
            if controls_me or self._dragged:
                event.used = True
                pass_event = False
                if event.pressed:
                    self._dragged = True
                    current_root_node.get().requires_size_recalculation = True
                    if event.pos.y < self.content_pos.y + self.content_size.y / 2:
                        delta = event.pos - self._last_mouse_pos
                        self.position += delta
                    else:
                        if event.pos.x > self.content_pos.x + self.content_size.y / 2:
                            delta = event.pos - self._last_mouse_pos
                            self.size += delta
                            point = self.position + self.size
                            root = current_root_node.get()
                            delta = point-(root.position+root.size)
                            if delta.x > 0:
                                self.size.x -= delta.x
                            if delta.y > 0:
                                self.size.y -= delta.y
                            if self.size.x < self.min_size.x:
                                self.size.x = self.min_size.x
                            if self.size.y < self.min_size.y:
                                self.size.y = self.min_size.y

                else:
                    self._dragged = False
            self._last_mouse_pos = event.pos
        
        if pass_event:
            super().handle_event(event)



class RootNodeB(NodeB):
    type = "root"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layers = dict()
        self.layer_priority = dict()
        self.requires_size_recalculation = False
        self.requested_update = None
        if current_root_node.get(None) is None:
            self.make_current()
    
    def recalc_if_needed(self):
        if self.requires_size_recalculation:
            self.recalc_size()

    @property
    def main_node(self):
        return self.layers["main"]

    @main_node.setter
    def main_node(self, value):
        self.layers["main"] = value

    def request_update_in(self, dt: float):
        if self.requested_update is None:
            self.requested_update = dt
        else:
            self.requested_update = min(self.requested_update, dt)

    def handle_event(self, event: GUIEvent):
        for chld in self.children:
            chld.handle_event(event)
            if event.used:
                break
    
    def set_layer_node(self, node, layer, priority=0):
        self.layers[layer] = node
        self.layer_priority[layer] = priority
        if not getattr(node, "ext_docked", True):
            node.position = (self.size - node.size) / 2 
        self.requires_size_recalculation = True
        for nd in self.layers.values():
            if hasattr(nd, "ext_set_focus"):
                nd.ext_set_focus(False)
        if hasattr(node, "ext_set_focus"):
            node.ext_set_focus(True)

    def del_node(self, node):
        for k, v in self.layers.items():
            if v is node:
                del self.layers[k]
                break

    @property
    def children(self):
        def get_layer_priority(layer):
            pr = self.layer_priority.get(layer, 0) + getattr(self.layers[layer], "ext_extra_priority", 0)
            if getattr(self.layers[layer], "ext_docked", True):
                pr -= 10
            return pr
        children = list()
        children_keys = list()
        children_keys.extend(self.layers.keys())
        children_keys.sort(key=get_layer_priority, reverse=True)
        for key in children_keys:
            children.append(self.layers[key])
        return children
    
    def recalc_size(self):
        self.requires_size_recalculation = False
        my_corner = self.position + self.size
        for chld in self.children:
            if getattr(chld, "ext_docked", True):
                chld.position = self.position
                chld.size = self.size
            else:
                chld_corner = chld.position + Vec2(chld.size.x, 20)
                if chld_corner.x > my_corner.x:
                    chld.position.x -= chld_corner.x-my_corner.x
                if chld_corner.y > my_corner.y:
                    chld.position.y -= chld_corner.y-my_corner.y
                if chld.position.x < self.position.x:
                    chld.position.x = self.position.x
                if chld.position.y < self.position.y:
                    chld.position.y = self.position.y
                if chld.size.x > self.size.x:
                    chld.size.x = self.size.x
                if chld.size.y > self.size.y:
                    chld.size.y = self.size.y
        super().recalc_size()
    
    def make_current(self):
        current_root_node.set(self)
    

current_root_node: ContextVar[RootNodeB] = ContextVar("current_root_node")