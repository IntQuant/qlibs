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
obj.load_path("C:/Users/IQuant/Desktop/menger.obj")

scene = Scene()

scene.light = Vec(0, 50, 0)
# print(obj.get_obj().materials['palette.001'].raw_params)

robj = RenderableModel(obj.get_obj(), scene, win.ctx)

running = True


proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)


used_time = 0
iters = 3000

while running:
    prev_time = time.process_time()
    # iters += 1
    ctx.clear(0, 0, 0)

    r = math.radians((time.time() * 10))

    d = 20

    view = Matrix4.look_at(
        Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0)
    )

    model = Matrix4.translation_matrix(0, 0, 0)
    model[0, 0] = 0.1
    model[1, 1] = 0.1
    model[2, 2] = 0.1

    robj.render(model, view, proj)

    for event in win.get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
    sdl2.SDL_GL_SwapWindow(win.window)
    used_time = time.process_time() - prev_time
    sdl2.SDL_Delay(10)


# iter_time_ms = used_time / iters * 1000

# print("Took %.3f ms per frame" % (iter_time_ms))
