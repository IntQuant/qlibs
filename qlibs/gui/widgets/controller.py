import glfw
from ...math import IVec
from .events import *

from collections import deque

spec_key_traversion_dict = { #TODO: add more keys
    glfw.KEY_BACKSPACE: "backspace"
}

class WindowWidgetController:
    def __init__(self):
        self.children = dict()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.selected = dict()

    def set_window_node(self, window, node):
        if hasattr(window, "window"):
            node.size = (window.width, window.height)
            node.recalc_size()
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        self.children[id_] = node
        self.selected[id_] = node

    def get_window_node(self, window):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        return self.children[id_]
    
    def set_selected_node(self, window, node):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        self.selected[id_] = node

    def get_selected_node(self, window):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        return self.selected[id_]

    def resize_handler(self, window, width, height):
        node = self.get_window_node(window)
        node.size = IVec(width, height)
        node.recalc_size()
    
    def send_mouse_event(self, window):
        event = MouseEvent(self.mouse_x, self.mouse_y, self.mouse_pressed)
        self.get_window_node(window).handle_event(event)

    def mouse_position_handler(self, window, x, y):
        node = self.get_window_node(window)
        self.mouse_x = x
        self.mouse_y = y
        self.send_mouse_event(window)
    
    def mouse_button_handler(self, window, button, action, mods):
        node = self.get_window_node(window)
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.mouse_pressed = action
        self.send_mouse_event(window)
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            self.check_reselect(window)
    
    def check_reselect(self, window):
        queue = deque()
        queue.append(self.get_window_node(window))
        cand = queue[0]
        mx, my = self.mouse_x, self.mouse_y
        while queue:
            current = queue.popleft()
            if current.selectable and 0 < mx - current.position.x < current.size.x and 0 < my - current.position.y < current.size.y:
                cand = current
            for child in current.children:
                queue.append(child)
        self.set_selected_node(window, cand)

    def key_handler(self, window, key, mods):
        event = KeyEvent(chr(key), mods)
        self.get_selected_node(window).handle_event(event)

    def spec_key_handler(self, window, key, ukey, pressed, mods):
        key = spec_key_traversion_dict.get(key, None)
        if pressed > 0 and key is not None:
            event = SpecKeyEvent(key, mods)
            self.get_selected_node(window).handle_event(event)

    def resize_handler(self, window, width, height):
        node = self.get_window_node(window)
        node.size = (width, height)
        node.recalc_size()

    def assign_to_window(self, win):
        win.mouse_motion_callback = self.mouse_position_handler
        win.mouse_button_callback = self.mouse_button_handler
        win.key_callback = self.key_handler
        win.spec_key_callback = self.spec_key_handler
        win.resize_callback = self.resize_handler
        
        node = self.get_window_node(win)
        node.size = win.width, win.height
        node.recalc_size()
        self.mouse_x, self.mouse_y = win.mouse_pos
        self.mouse_pressed = False

    
    def unassign_from_window(self, win):
        win.mouse_motion_callback = None
        win.mouse_button_callback = None
        win.key_callback = None
        win.resize_callback = None
        win.spec_key_callback = None
    
    
