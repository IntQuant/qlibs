import time
import math
from array import array

import moderngl
import sdl2
from PIL import Image

from qlibs.vec import Vec
from qlibs.matrix import Matrix4, IDENTITY
from qlibs.gui.window_provider import window_provider
from qlibs.util import try_write
from qlibs import modelloader
from qlibs import resource_loader
from qlibs.modelrenderer import RenderableModel, Scene

width = 800
height = 600
resource_loader.search_locations.append("C:/Users/IQuant/Desktop/models")


win = window_provider.Window()
ctx = win.ctx

obj = modelloader.OBJLoader()
obj.load_path("C:/Users/IQuant/Desktop/models/menger.obj")

scene = Scene()
robj = RenderableModel(obj.get_obj(), scene, win.ctx)

running = True

proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)

used_time = 0
iters = 100


def render():
    prev_time = time.process_time()
    ctx.clear(0, 0, 0)

    r = math.radians((time.time() * 10))

    d = 50

    view = Matrix4.look_at(
        Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0)
    )

    for i in range(100):

        model = Matrix4.translation_matrix(0, 0, i * 20)

        robj.render(model, view, proj)

    for event in win.get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
    sdl2.SDL_GL_SwapWindow(win.window)
    used_time = time.process_time() - prev_time
    # sdl2.SDL_Delay(10)
    return used_time


# ctx.enable(moderngl.DEPTH_TEST)

for i in range(10):
    render()

from tqdm import tqdm, trange

for i in trange(iters):
    used_time += render()

iter_time_ms = used_time / iters * 1000

print("Took %.3f ms per frame" % (iter_time_ms))
