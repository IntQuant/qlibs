from typing import Callable
import glfw
from ...math import IVec
from .events import *
import logging
logger = logging.getLogger("qlibs|window_controller")
#logger.setLevel(logging.DEBUG)
from contextvars import ContextVar

from collections import deque

spec_key_traversion_dict_old = {
    glfw.KEY_BACKSPACE: "backspace",
    glfw.KEY_LEFT: "left",
    glfw.KEY_RIGHT: "right",
    glfw.KEY_UP: "up",
    glfw.KEY_DOWN: "down",
    glfw.KEY_ENTER: "enter",
    glfw.KEY_C: "c",
    glfw.KEY_V: "v",
}

is_selected_cb: ContextVar[Callable] = ContextVar("is_selected_cb")

spec_key_traversion_dict = {
    glfw.KEY_0: '0',
    glfw.KEY_1: '1',
    glfw.KEY_2: '2',
    glfw.KEY_3: '3',
    glfw.KEY_4: '4',
    glfw.KEY_5: '5',
    glfw.KEY_6: '6',
    glfw.KEY_7: '7',
    glfw.KEY_8: '8',
    glfw.KEY_9: '9',
    glfw.KEY_A: 'a',
    glfw.KEY_APOSTROPHE: 'apostrophe',
    glfw.KEY_B: 'b',
    glfw.KEY_BACKSLASH: 'backslash',
    glfw.KEY_BACKSPACE: 'backspace',
    glfw.KEY_C: 'c',
    glfw.KEY_CAPS_LOCK: 'caps_lock',
    glfw.KEY_COMMA: 'comma',
    glfw.KEY_D: 'd',
    glfw.KEY_DELETE: 'delete',
    glfw.KEY_DOWN: 'down',
    glfw.KEY_E: 'e',
    glfw.KEY_END: 'end',
    glfw.KEY_ENTER: 'enter',
    glfw.KEY_EQUAL: 'equal',
    glfw.KEY_ESCAPE: 'escape',
    glfw.KEY_F: 'f',
    glfw.KEY_F1: 'f1',
    glfw.KEY_F10: 'f10',
    glfw.KEY_F11: 'f11',
    glfw.KEY_F12: 'f12',
    glfw.KEY_F13: 'f13',
    glfw.KEY_F14: 'f14',
    glfw.KEY_F15: 'f15',
    glfw.KEY_F16: 'f16',
    glfw.KEY_F17: 'f17',
    glfw.KEY_F18: 'f18',
    glfw.KEY_F19: 'f19',
    glfw.KEY_F2: 'f2',
    glfw.KEY_F20: 'f20',
    glfw.KEY_F21: 'f21',
    glfw.KEY_F22: 'f22',
    glfw.KEY_F23: 'f23',
    glfw.KEY_F24: 'f24',
    glfw.KEY_F25: 'f25',
    glfw.KEY_F3: 'f3',
    glfw.KEY_F4: 'f4',
    glfw.KEY_F5: 'f5',
    glfw.KEY_F6: 'f6',
    glfw.KEY_F7: 'f7',
    glfw.KEY_F8: 'f8',
    glfw.KEY_F9: 'f9',
    glfw.KEY_G: 'g',
    glfw.KEY_GRAVE_ACCENT: 'grave_accent',
    glfw.KEY_H: 'h',
    glfw.KEY_HOME: 'home',
    glfw.KEY_I: 'i',
    glfw.KEY_INSERT: 'insert',
    glfw.KEY_J: 'j',
    glfw.KEY_K: 'k',
    glfw.KEY_KP_0: 'kp_0',
    glfw.KEY_KP_1: 'kp_1',
    glfw.KEY_KP_2: 'kp_2',
    glfw.KEY_KP_3: 'kp_3',
    glfw.KEY_KP_4: 'kp_4',
    glfw.KEY_KP_5: 'kp_5',
    glfw.KEY_KP_6: 'kp_6',
    glfw.KEY_KP_7: 'kp_7',
    glfw.KEY_KP_8: 'kp_8',
    glfw.KEY_KP_9: 'kp_9',
    glfw.KEY_KP_ADD: 'kp_add',
    glfw.KEY_KP_DECIMAL: 'kp_decimal',
    glfw.KEY_KP_DIVIDE: 'kp_divide',
    glfw.KEY_KP_ENTER: 'kp_enter',
    glfw.KEY_KP_EQUAL: 'kp_equal',
    glfw.KEY_KP_MULTIPLY: 'kp_multiply',
    glfw.KEY_KP_SUBTRACT: 'kp_subtract',
    glfw.KEY_L: 'l',
    glfw.KEY_LAST: 'last',
    glfw.KEY_LEFT: 'left',
    glfw.KEY_LEFT_ALT: 'left_alt',
    glfw.KEY_LEFT_BRACKET: 'left_bracket',
    glfw.KEY_LEFT_CONTROL: 'left_control',
    glfw.KEY_LEFT_SHIFT: 'left_shift',
    glfw.KEY_LEFT_SUPER: 'left_super',
    glfw.KEY_M: 'm',
    glfw.KEY_MENU: 'menu',
    glfw.KEY_MINUS: 'minus',
    glfw.KEY_N: 'n',
    glfw.KEY_NUM_LOCK: 'num_lock',
    glfw.KEY_O: 'o',
    glfw.KEY_P: 'p',
    glfw.KEY_PAGE_DOWN: 'page_down',
    glfw.KEY_PAGE_UP: 'page_up',
    glfw.KEY_PAUSE: 'pause',
    glfw.KEY_PERIOD: 'period',
    glfw.KEY_PRINT_SCREEN: 'print_screen',
    glfw.KEY_Q: 'q',
    glfw.KEY_R: 'r',
    glfw.KEY_RIGHT: 'right',
    glfw.KEY_RIGHT_ALT: 'right_alt',
    glfw.KEY_RIGHT_BRACKET: 'right_bracket',
    glfw.KEY_RIGHT_CONTROL: 'right_control',
    glfw.KEY_RIGHT_SHIFT: 'right_shift',
    glfw.KEY_RIGHT_SUPER: 'right_super',
    glfw.KEY_S: 's',
    glfw.KEY_SCROLL_LOCK: 'scroll_lock',
    glfw.KEY_SEMICOLON: 'semicolon',
    glfw.KEY_SLASH: 'slash',
    glfw.KEY_SPACE: 'space',
    glfw.KEY_T: 't',
    glfw.KEY_TAB: 'tab',
    glfw.KEY_U: 'u',
    glfw.KEY_UNKNOWN: 'unknown',
    glfw.KEY_UP: 'up',
    glfw.KEY_V: 'v',
    glfw.KEY_W: 'w',
    glfw.KEY_WORLD_1: 'world_1',
    glfw.KEY_WORLD_2: 'world_2',
    glfw.KEY_X: 'x',
    glfw.KEY_Y: 'y',
    glfw.KEY_Z: 'z',
}

def null_event_handler(event): pass

class WindowWidgetController:
    """
    Converts events from glfw window to qlibs format and sends them to nodes.

    **additional_event_handler** field will be called when event wasn't used. If **force_send_events** is set to True it will be called anyway.
    """
    def __init__(self):
        self.children = dict()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.selected = dict()
        self.pressed_buttons = set()
        self.additional_event_handler = null_event_handler
        self.force_send_events = False

    def set_window_node(self, window, node):
        if hasattr(window, "window"):
            node.size = (window.width, window.height)
            node.recalc_size()
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        self.children[id_] = node
        self.selected[id_] = None

    def get_window_node(self, window):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        try:
            return self.children[id_]
        except KeyError as e:
            raise RuntimeError("No node assigned to window") from e
    
    def set_selected_node(self, window, node):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        self.selected[id_] = node
        logger.debug(self.selected)

    def get_selected_node(self, window):
        if hasattr(window, "window"):
            window = window.window
        id_ = glfw.get_window_user_pointer(window)
        return self.selected[id_]

    def resize_handler(self, window, width, height):
        node = self.get_window_node(window)
        node.size = IVec(width, height)
        node.recalc_size()
    
    def send_mouse_event(self, window, scroll_y=0):
        up = scroll_y > 0
        down = scroll_y < 0
        event = MouseEvent(self.mouse_x, self.mouse_y, self.mouse_pressed, up, down, pressed_buttons=self.pressed_buttons)
        self.get_window_node(window).handle_event(event)
        if self.force_send_events or not event.used:
            self.additional_event_handler(event)

    def mouse_position_handler(self, window, x, y):
        self.mouse_x, self.mouse_y = window.mouse_pos_flipped
        self.send_mouse_event(window)
    
    def mouse_button_handler(self, window, button, action, mods):
        logger.debug("mouse button event")
        self.last_mods = KeyMods(mods)
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.mouse_pressed = action
        if action == glfw.PRESS:
            self.pressed_buttons.add(button)
        else:
            self.pressed_buttons.discard(button)
        self.send_mouse_event(window)
        if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
            self.check_reselect(window)
    
    def scroll_handler(self, window, x, y):
        self.send_mouse_event(window, scroll_y=y)

    def handle_to_selected(self, window, event):
        node = self.get_selected_node(window)
        logger.debug("Sent %s to %s (window %s)", event, node, window)
        if node is not None:
            node.handle_event(event)
        if node is None or self.force_send_events:
            self.additional_event_handler(event)

    def check_reselect(self, window):
        logger.debug("Checking reselection in %s", window)
        queue = deque()
        queue.append(self.get_window_node(window))
        cand = None
        mx, my = self.mouse_x, self.mouse_y
        found_window = False
        while queue:
            current = queue.pop()
            if current.type == "window":
                if found_window:
                    break
                if 0 < mx - current.position.x < current.size.x and 0 < my - current.position.y < current.size.y:
                    found_window = True

            if current.selectable and 0 < mx - current.position.x < current.size.x and 0 < my - current.position.y < current.size.y:
                cand = current
            for child in current.children:
                queue.append(child)
        logger.debug("Selected %s", cand)
        self.set_selected_node(window, cand)

    def key_handler(self, window, key, mods):
        event = KeyEvent(chr(key), KeyMods(mods))
        self.handle_to_selected(window, event)

    def spec_key_handler(self, window, key, ukey, pressed, mods):
        key = spec_key_traversion_dict.get(key, None)
        if pressed > 0 and key is not None:
            event = SpecKeyEvent(key, KeyMods(mods))
            self.handle_to_selected(window, event)

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
        win.scroll_callback = self.scroll_handler
        
        node = self.get_window_node(win)
        node.size = win.width, win.height
        node.recalc_size()
        self.mouse_x, self.mouse_y = win.mouse_pos_flipped
        self.mouse_pressed = False

    def unassign_from_window(self, win):
        win.mouse_motion_callback = None
        win.mouse_button_callback = None
        win.key_callback = None
        win.resize_callback = None
        win.spec_key_callback = None
        win.scroll_callback = None
    
    def is_node_selected(self, node):
        return node in self.selected.values()
    
    def make_current(self):
        is_selected_cb.set(self.is_node_selected)
    
    
