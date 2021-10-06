"""
This example shows how to load images into SpriteMaster without using qlibs' resource system.
It also shows how texture filter can be specified.
"""

from qlibs.highlevel.graphics import SpriteMaster
from qlibs.gui.window import Window
import moderngl
from PIL import Image, ImageDraw

image = Image.radial_gradient("L").convert("RGBA").resize((16, 16))
drawer = ImageDraw.Draw(image)
drawer.line(((0, 0, 8, 8)))

win = Window(width=1220)
sprite_master = SpriteMaster(win.ctx)
sprite_master_2 = SpriteMaster(win.ctx, texture_filter=(moderngl.NEAREST, moderngl.NEAREST))
sprite_master.load_image("grad", image)
sprite_master_2.load_image("grad", image)
sprite_master.init()
sprite_master_2.init()

while not win.should_close:
    sprite_master.add_sprite_centered("grad", -250, 0, 450, 450)
    sprite_master_2.add_sprite_centered("grad", 250, 0, 450, 450)
    sprite_master.render_centered((0, 0), win.size)
    sprite_master_2.render_like(sprite_master)
    win.swap()
    win.wait_events()
