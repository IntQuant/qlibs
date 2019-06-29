import time
import math
#import colorsys
import random

import moderngl

from qlibs.gui.window import Window
from qlibs.gui.basic_shapes import ShapeDrawer

win = Window(500, 500)

random.seed(1)

drawer = ShapeDrawer(win.ctx)

def rgb(r, g, b):
    return r / 256, g / 256, b / 256

for i in range(0, 360, 5):
    r = math.radians(i)
    r0 = r
    color = random.choice([rgb(0, 255, 68), rgb(255, 68, 0), rgb(68, 70, 255)])
    d = 0.3
    drawer.add_line((math.sin(r0), math.cos(r0)), (math.sin(r)*d, math.cos(r)*d), color=color)

#win.ctx.enable(moderngl.BLEND)

while not win.should_close:
    win.ctx.clear(0, 0, 0)
    drawer.render(reset=False)
    win.swap()
    win.poll_events()
    time.sleep(0.05)