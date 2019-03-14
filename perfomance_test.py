import time
import math
import logging

logging.basicConfig(level=logging.DEBUG)
 
import moderngl

from qlibs import resource_loader, resource_manager
from qlibs.vec import MVec as Vec
from qlibs.matrix import Matrix4, IDENTITY
from qlibs.gui.window_provider import window_provider
from qlibs.models.modelrenderer import RenderableModel, Scene
from qlibs.gui.basic_shapes import ShapeDrawer

import sdl2  # Needs to be imported *after* window_provider

# Add models to resource locations
resource_loader.search_locations.append("C:/Users/IQuant/Desktop/models")
# Create window
win = window_provider.Window()
ctx = win.ctx
# Create scene
#scene = Scene()
# Load model
# Upgrade model to renderable
#robj = RenderableModel(resource_manager.load_model("test2.obj"), scene, win.ctx)

running = True
drawer = ShapeDrawer(ctx)

frames_left = 1000

# Main loop
while running:
    if frames_left <= 0:
        break
    frames_left -= 1
    
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
    #robj.render(model, view, proj)
    
    #drawer.add_triangle(((0, 0), (0, 1), (1, 0)), (0.5, 1, 1., 1.))
    #drawer.add_polygon(((0, 0), (0, 1), (1, 1), (1, 0)), (0.5, 1, 1., 1.))
    for i in range(10):
        drawer.add_rectangle(-0.5+i*0.1, 0.3, 0.05, 0.1)
    drawer.render()
    # Iterate events
    for event in win.get_events():
        # Closing event
        if event.type == sdl2.SDL_QUIT:
            running = False
    # Swap screen buffers
    win.swap()
    # Delay
    #sdl2.SDL_Delay(10)
