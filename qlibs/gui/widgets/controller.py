import glfw
from ...math import IVec
from .events import *

class WindowWidgetController:
    def __init__(self):
        self.children = dict()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False

    def set_window_node(self, window, node):
        if hasattr(window, "window"):
            node.size = (window.width, window.height)
            node.recalc_size()
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        self.children[id_] = node

    def get_window_node(self, window):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        return self.children[id_]

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
            self.mouse_pressed = action == glfw.PRESS
        self.send_mouse_event(window)

    def resize_handler(self, window, width, height):
        node = self.get_window_node(window)
        node.size = (width, height)
        node.recalc_size()

    def assign_to_window(self, win):
        win.mouse_motion_callback = self.mouse_position_handler
        win.mouse_button_callback = self.mouse_button_handler
        win.resize_callback = self.resize_handler
        
        node = self.get_window_node(win)
        node.size = win.width, win.height
        node.recalc_size()

    
    def unassign_from_window(self, win):
        win.mouse_motion_callback = None
        win.mouse_button_callback = None
        win.resize_callback = None
    
    
