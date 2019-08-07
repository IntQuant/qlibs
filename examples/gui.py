from qlibs.gui.widgets.behaviors import *
from qlibs.gui.widgets.controller import WindowWidgetController
from qlibs.gui.widgets.render import DefaultRenderer
from qlibs.gui.window import Window
import time
import moderngl

win = Window()
ctrl = WindowWidgetController()

centerer = CentererB(100, 100)
placer = ColumnPlacerB()

for i in range(5):
    button = ButtonB(f"{i}", lambda x: print(f"hi from {x}"), text=f"Текст на кнопке {i}")
    c = CentererB(10, 10)
    c.add_child(button)
    placer.add_child(c)

centerer.add_child(placer)

ctrl.set_window_node(win, centerer)
ctrl.assign_to_window(win)
rend = DefaultRenderer(win, centerer)

while not win.should_close:
    win.ctx.clear(0, 0, 0)
    win.ctx.enable_only(moderngl.BLEND)
    rend.render()
    win.swap()
    win.wait_events()
    #win.poll_events()
    #time.sleep(0.05)
