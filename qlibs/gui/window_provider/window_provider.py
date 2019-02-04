"""
  Module that provides opengl-enabled windows
"""

try:
    from ... import resource_loader
except ValueError:
    from .. import resource_loader
except ImportError:
    from .. import resource_loader

import moderngl

resource_loader.ensure_sdl2_install()

import sdl2  # PySDL2
import ctypes


class Window:
    """Basic window class"""

    def __init__(self, request=330, win_name=b"qlibs", width=800, height=600):
        """
          *request* - OpenGL version to use
          *win_name* - name of the window
          *width* - window width
          *height* - window height
        """
        self.window = sdl2.SDL_CreateWindow(
            win_name,
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            sdl2.SDL_WINDOW_OPENGL,
        )

        sdl2.SDL_SetWindowResizable(self.window, True)

        self.context = sdl2.SDL_GL_CreateContext(self.window)

        self.event = sdl2.SDL_Event()

        self.ctx = moderngl.create_context(request)

    def get_events(self):
        """
          Iterate over recent events
        """
        while sdl2.SDL_PollEvent(ctypes.byref(self.event)) != 0:
            yield self.event
