"""
  Module that provides opengl-enabled windows
"""

import ctypes
import moderngl

from ... import resource_loader
resource_loader.ensure_sdl2_install()

import sdl2  # PySDL2 - needs to be imported after resource_loader




class Window:
    """Basic window class"""

    def __init__(
        self,
        request=330,
        win_name=b"qlibs",
        width=800,
        height=600,
        params=sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_RESIZABLE,
    ):
        """
          *request* - OpenGL version to use
          *win_name* - name of the window
          *width* - window width
          *height* - window height
          *params* - window parameters
        """
        self.window = sdl2.SDL_CreateWindow(
            win_name,
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            params,
        )
        sdl2.SDL_SetWindowResizable(self.window, True)
        self.context = sdl2.SDL_GL_CreateContext(self.window)
        self.event = sdl2.SDL_Event()
        self.ctx = moderngl.create_context(request)

    def get_events(self):
        """Iterate over recent events"""
        while sdl2.SDL_PollEvent(ctypes.byref(self.event)) != 0:
            yield self.event
    
    def swap(self):
        """Swap window buffers"""
        size = self.get_size()
        self.ctx.viewport = (0, 0, size[0], size[1])
        sdl2.SDL_GL_SwapWindow(self.window)
        
        
    def get_size(self):
        """Get window size"""
        x = ctypes.c_int(0)
        y = ctypes.c_int(0)
        sdl2.SDL_GetWindowSize(self.window, x, y)
        return x.value, y.value
