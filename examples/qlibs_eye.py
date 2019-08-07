import time
import math
#import colorsys
import random

import moderngl

from qlibs.gui.window import Window
from qlibs.gui.basic_shapes import ShapeDrawer

sizemult = 4

win = Window(50*sizemult, 50*sizemult)

random.seed(1)

drawer = ShapeDrawer(win.ctx)

def rgb(r, g, b, a=256):
    return r / 256, g / 256, b / 256, a / 256

for i in range(0, 360, 5):
    r = math.radians(i)
    r0 = r+0.5
    color = random.choice([rgb(0, 255, 68), rgb(255, 68, 0), rgb(68, 70, 255)])
    d = 0.3
    d0 = 0.4
    drawer.add_line((math.sin(r0)*d0, math.cos(r0)*d0), (math.sin(r)*d, math.cos(r)*d), color=color)

#win.ctx.enable(moderngl.BLEND)

while not win.should_close:
    win.ctx.clear(0, 0, 0)
    drawer.render(reset=False)
    win.swap()
    win.poll_events()
    time.sleep(0.05)

framebuf = win.ctx.framebuffer([win.ctx.renderbuffer(size=(50*sizemult, 50*sizemult))])
framebuf.use()
drawer.render()

from PIL import Image
img = Image.frombytes("RGB", (50*sizemult, 50*sizemult), framebuf.read()).crop((10*sizemult, 10*sizemult, 40*sizemult, 40*sizemult))
img.save("eye0.png")