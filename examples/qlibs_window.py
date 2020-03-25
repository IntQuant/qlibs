"""
  Using window directly
"""

import time

from qlibs.gui.window import Window
from qlibs.gui.basic_shapes import ShapeDrawer

win = Window(1600, 1200)

drawer = ShapeDrawer(win.ctx)

while not win.should_close:
    win.ctx.clear(0, 0, 0)
    drawer.add_line((-1, -1), (1, 1))
    drawer.render()
    win.swap()
    win.poll_events()
    time.sleep(0.05)