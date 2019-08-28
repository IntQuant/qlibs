import glfw
import moderngl

default_hint_conf = {
    glfw.CONTEXT_VERSION_MAJOR: 3,
    glfw.CONTEXT_VERSION_MINOR: 3,
    glfw.DOUBLEBUFFER: True,
    glfw.DEPTH_BITS: 24,
    glfw.CONTEXT_CREATION_API: glfw.NATIVE_CONTEXT_API,
    glfw.CLIENT_API: glfw.OPENGL_API,
    glfw.OPENGL_PROFILE: glfw.OPENGL_CORE_PROFILE,
    glfw.RESIZABLE: True,
    glfw.OPENGL_FORWARD_COMPAT: True,
    glfw.SAMPLES: 4,
}

class Window:
    def __init__(self, width=800, height=600, title="QLibs window", swap_interval=1, hint_conf=default_hint_conf):
        self.width = width
        self.height = height
        self.resize_callback = None
        self.mouse_motion_callback = None
        self.mouse_button_callback = None
        self.scroll_callback = None
        self.key_callback = None
        self.spec_key_callback = None
        self.flip_mouse_y = True #flipped relativly to usual math-y respresentation

        glfw.init()
        for k, v in hint_conf.items():
            glfw.window_hint(k, v)
        
        self.window = glfw.create_window(width, height, title, None, None)
        glfw.set_window_user_pointer(self.window, id(self.window))
        glfw.make_context_current(self.window)
        glfw.swap_interval(swap_interval)
        #callbacks
        glfw.set_window_size_callback(self.window, self.on_resize)
        glfw.set_framebuffer_size_callback(self.window, self.update_viewport)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_motion)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_char_mods_callback(self.window, self.on_key_press)
        glfw.set_key_callback(self.window, self.on_spec_key_press)
        glfw.set_scroll_callback(self.window, self.on_scroll)

        self.ctx = moderngl.create_context()

    def on_resize(self, win, width, height):
        self.width = width
        self.height = height
        if self.resize_callback:
            self.resize_callback(win, width, height)
    
    def update_viewport(self, window, width, height):
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
    
    def on_scroll(self, window, x, y):
        if self.scroll_callback:
            self.scroll_callback(window, x, y)

    def on_mouse_motion(self, window, x, y):
        if self.mouse_motion_callback:
            if self.flip_mouse_y:
                self.mouse_motion_callback(window, x, y)
            else:
                self.mouse_motion_callback(window, x, self.height - y)

    def on_mouse_button(self, window, button, action, mods):
        if self.mouse_button_callback:
            self.mouse_button_callback(window, button, action == glfw.PRESS, mods)
        
    def is_key_pressed(self, key):
        return glfw.get_key(self.window, key)
    
    def is_mouse_pressed(self, key):
        return glfw.get_mouse_button(self.window, key)
    
    def on_key_press(self, window, key, mods):
        if self.key_callback:
            self.key_callback(window, key, mods)
    
    def on_spec_key_press(self, window, key, ukey, pressed, mods):
        if self.spec_key_callback:
            self.spec_key_callback(window, key, ukey, pressed, mods)

    def enable_sticky_mouse(self, action=True):
        glfw.set_input_mode(self.window, glfw.STICKY_MOUSE_BUTTONS, action)

    


    
