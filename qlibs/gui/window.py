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
    glfw.SAMPLES: 4*4,
}

class Window:
    def __init__(self, width=800, height=600, title="QLibs window", swap_interval=1, hint_conf=default_hint_conf):
        self.width = width
        self.height = height
        
        glfw.init()
        for k, v in hint_conf.items():
            glfw.window_hint(k, v)
        
        
        
        self.window = glfw.create_window(width, height, title, None, None)
        glfw.make_context_current(self.window)
        glfw.swap_interval(swap_interval)
        glfw.set_window_size_callback(self.window, self.on_resize)
        self.ctx = moderngl.create_context()

    def on_resize(self, win, width, height):
        self.width = width
        self.height = height
        self.update_viewport()

    
    def update_viewport(self):
        self.ctx.viewport = (0, 0, self.width, self.height)
    
    def swap(self):
        glfw.swap_buffers(self.window)
    
    def poll_events(self):
        glfw.poll_events()

    @property
    def should_close(self):
        return glfw.window_should_close(self.window)
        
