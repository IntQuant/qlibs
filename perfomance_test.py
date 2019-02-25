import ctypes
import time
import math
from array import array

import moderngl
from PIL import Image

from qlibs.vec import Vec
from qlibs.matrix import Matrix4, IDENTITY
from qlibs.gui.window_provider import window_provider
from qlibs.util import try_write
from qlibs import modelloader
from qlibs import resource_loader
from qlibs.modelrenderer import RenderableModel, Scene

import sdl2  # Needs to be imported *after* window_provider

# Add models to resource locations
resource_loader.search_locations.append("C:/Users/IQuant/Desktop/models")
# Create window
win = window_provider.Window()
ctx = win.ctx
# Create scene
scene = Scene()
# Load model
obj = modelloader.OBJLoader()
obj.load_path(resource_loader.get_res_path("test2.obj"))
# Upgrade model to renderable
robj = RenderableModel(obj.get_obj(), scene, win.ctx)

running = True
# Main loop
while running:
    width, height = win.get_size()
    # Make projection matrix
    proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)
    # Clear frame
    ctx.clear(0, 0, 0)
    d = 40
    r = math.radians((time.time() * 50))
    # Make view matrix
    view = Matrix4.look_at(
        Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0)
    )
    # Make model matrix
    model = Matrix4.translation_matrix(0, 0, 0)
    # Render model
    robj.render(model, view, proj)
    # Iterate events
    for event in win.get_events():
        # Closing event
        if event.type == sdl2.SDL_QUIT:
            running = False
    # Swap screen buffers
    win.swap()
    # Delay
    sdl2.SDL_Delay(10)
