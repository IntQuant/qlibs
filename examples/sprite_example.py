from qlibs.gui.window import Window
from qlibs.resources.resource_loader import get_image_data, add_loader, SearchLocationLoader
from qlibs.gui.sprite_drawer import SpriteDrawer
from qlibs.math import Matrix4
import time

import moderngl

add_loader(SearchLocationLoader("/home/iquant/Документы"))

win = Window()
img = get_image_data("ShiftingSword.png", mode="RGBA")

#win.ctx.wireframe = True

for key in [
    'GL_VENDOR',
    'GL_RENDERER',
    'GL_VERSION',
    'GL_MAX_ARRAY_TEXTURE_LAYERS',
]:
    print(key, win.ctx.info[key])
    

drawer = SpriteDrawer(win.ctx, (64, 64, 1), img.data)

size = 64

while not win.should_close:
    drawer.add_sprite_rect(0, 0, 0, size, size)
    drawer.add_sprite_rotated(0, 128, 128, 64, 64, time.time())
    win.ctx.enable(moderngl.BLEND)
    win.ctx.clear(0.5, 0.5, 0.5)
    mvp = Matrix4.orthogonal_projection(0, win.width, 0, win.height, -1, 1)
    drawer.render(mvp=mvp, reset=True)
    win.swap()
    win.wait_events()
