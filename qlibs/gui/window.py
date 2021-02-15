import glfw
import moderngl
from contextvars import ContextVar

import logging
logger = logging.getLogger("qlibs.gui.window")

default_hint_conf = {
    glfw.CONTEXT_VERSION_MAJOR: 3,
    glfw.CONTEXT_VERSION_MINOR: 3,
    glfw.DOUBLEBUFFER: True,
    glfw.DEPTH_BITS: 24,
    glfw.CONTEXT_CREATION_API: glfw.NATIVE_CONTEXT_API,
    glfw.CLIENT_API: glfw.OPENGL_API,
    glfw.OPENGL_PROFILE: glfw.OPENGL_CORE_PROFILE,
    glfw.OPENGL_FORWARD_COMPAT: True,
    glfw.SAMPLES: 4,
    glfw.REFRESH_RATE: 60,
}


fallback_hint_conf = {
    glfw.CONTEXT_VERSION_MAJOR: 3,
    glfw.CONTEXT_VERSION_MINOR: 3,
    glfw.DOUBLEBUFFER: True,
    glfw.DEPTH_BITS: 8,
    glfw.CONTEXT_CREATION_API: glfw.NATIVE_CONTEXT_API,
    glfw.CLIENT_API: glfw.OPENGL_API,
    glfw.SAMPLES: 1,
}

class Window:
    def __init__(self, width=800, height=600, title="QLibs window", swap_interval=1, hint_conf=default_hint_conf, resizable=True, fullscreen=False, transparent=False):
        self.width = width
        self.height = height
        self.resize_callback = None
        self.mouse_motion_callback = None
        self.mouse_button_callback = None
        self.scroll_callback = None
        self.key_callback = None
        self.spec_key_callback = None
        self.flip_mouse_y = False #flipped relativly to usual math-y respresentation

        glfw.init()
        glfw.window_hint(glfw.RESIZABLE, resizable and not fullscreen)
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, transparent)
        for k, v in hint_conf.items():
            glfw.window_hint(k, v)
        monitor = None
        if fullscreen:
            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            width = mode.size.width
            height = mode.size.height
            #width = 1920
            #height = 1080
            glfw.window_hint(glfw.RED_BITS, mode.bits.red)
            glfw.window_hint(glfw.GREEN_BITS, mode.bits.green)
            glfw.window_hint(glfw.BLUE_BITS, mode.bits.blue)
            glfw.window_hint(glfw.REFRESH_RATE, mode.refresh_rate)
            
        try:
            self.window = glfw.create_window(width, height, title, monitor, None)
        except glfw.GLFWError:
            logger.warn("Provided config is unavailable, using fallback config")
            glfw.default_window_hints()
            for k, v in fallback_hint_conf.items():
                glfw.window_hint(k, v)
            self.window = glfw.create_window(width, height, title, None, None)
        
        if fullscreen:
            self.width, self.height = glfw.get_framebuffer_size(self.window) #Required on windows

        glfw.set_window_user_pointer(self.window, id(self.window))
        glfw.make_context_current(self.window)
        glfw.swap_interval(swap_interval)
        #callbacks
        glfw.set_window_size_callback(self.window, self._on_resize)
        glfw.set_framebuffer_size_callback(self.window, self._update_viewport)
        glfw.set_cursor_pos_callback(self.window, self._on_mouse_motion)
        glfw.set_mouse_button_callback(self.window, self._on_mouse_button)
        glfw.set_char_mods_callback(self.window, self._on_key_press)
        glfw.set_key_callback(self.window, self._on_spec_key_press)
        glfw.set_scroll_callback(self.window, self._on_scroll)

        try:
            self.ctx = moderngl.create_context()
        except:
            self.ctx = moderngl.create_context(libgl='libGL.so.1')

    def make_context_current(self):
        current_window.set(self)
        current_context.set(self.ctx)
        glfw.make_context_current(self.window)

    def _on_resize(self, win, width, height):
        self.width = width
        self.height = height
        if self.resize_callback:
            self.resize_callback(win, width, height)
    
    def _update_viewport(self, window, width, height):
        self.ctx.viewport = (0, 0, width, height)
    
    def swap(self):
        glfw.swap_buffers(self.window)
    
    def poll_events(self):
        glfw.poll_events()
    
    def wait_events(self, timeout=None):
        if timeout is None:
            glfw.wait_events()
        else:
            glfw.wait_events_timeout(timeout)

    @property
    def should_close(self):
        return glfw.window_should_close(self.window)

    @should_close.setter
    def should_close(self, x):
        glfw.set_window_should_close(self.window, x)
    
    def close(self):
        glfw.destroy_window(self.window)

    @property
    def mouse_pos(self):
        x, y = glfw.get_cursor_pos(self.window)
        if self.flip_mouse_y:
            return x, y    
        else:
            return x, self.height-y

    @property
    def mouse_pos_normal(self):
        x, y = glfw.get_cursor_pos(self.window)
        return x, self.height-y

    @property
    def mouse_pos_flipped(self):
        x, y = glfw.get_cursor_pos(self.window)
        return x, y

    @property
    def size(self):
        return (self.width, self.height)
    
    def _on_scroll(self, window, x, y):
        if self.scroll_callback:
            self.scroll_callback(self, x, y)

    def _on_mouse_motion(self, window, x, y):
        if self.mouse_motion_callback:
            if self.flip_mouse_y:
                self.mouse_motion_callback(self, x, y)
            else:
                self.mouse_motion_callback(self, x, self.height - y)

    def _on_mouse_button(self, window, button, action, mods):
        if self.mouse_button_callback:
            self.mouse_button_callback(self, button, action == glfw.PRESS, mods)
        
    def is_key_pressed(self, key):
        return glfw.get_key(self.window, key)
    
    def is_mouse_pressed(self, key):
        return glfw.get_mouse_button(self.window, key)
    
    def _on_key_press(self, window, key, mods):
        if self.key_callback:
            self.key_callback(self, key, mods)
    
    def _on_spec_key_press(self, window, key, ukey, pressed, mods):
        if self.spec_key_callback:
            self.spec_key_callback(self, key, ukey, pressed, mods)

    def enable_sticky_mouse(self, action=True):
        glfw.set_input_mode(self.window, glfw.STICKY_MOUSE_BUTTONS, action)

    
current_context: ContextVar[moderngl.Context] = ContextVar("current_context")
current_window: ContextVar[Window] = ContextVar("current_window")

    
