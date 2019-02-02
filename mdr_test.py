from qlibs.vec import Vec
from qlibs.matrix import Matrix4, IDENTITY
from qlibs.gui.window_provider import window_provider
from qlibs.util import try_write
from qlibs import modelloader
from qlibs import resource_loader
from qlibs.modelrenderer import RenderableModel, Scene

import moderngl
import sdl2
from PIL import Image

import time
import math
from array import array



width = 800
height = 600
resource_loader.search_locations.append("C:/Users/IQuant/Desktop")


win = window_provider.Window()
ctx = win.ctx

obj = modelloader.OBJLoader()
obj.load_path("C:/Users/IQuant/Desktop/test2.obj")

scene = Scene()

print(obj.get_obj().materials['palette.001'].raw_params)

robj = RenderableModel(obj.get_obj(), scene, win.ctx)

running = True



proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)

while running:
    ctx.clear(0, 0, 0)
    
    r = math.radians((time.time() * 10))

    d = 50
    
    view = Matrix4.look_at(Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0))
    
    model = Matrix4.translation_matrix(0, 0, 0)
    
    robj.render(model, view, proj)
    
    for event in win.get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
        #print(event.type)
    sdl2.SDL_GL_SwapWindow(win.window)
    sdl2.SDL_Delay(10)

