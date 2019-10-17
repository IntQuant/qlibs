from qlibs.gui.widgets.behaviors import *
from qlibs.gui.widgets.app import App
#from qlibs.gui.widgets.controller import WindowWidgetController
#from qlibs.gui.widgets.render import DefaultRenderer
#from qlibs.gui.window import Window
import time
import moderngl



centerer = CentererB(100, 100)
placer = ColumnPlacerB()
#placer.spc = 20
bplacer = ScrollableListB()
for i in range(20):
    button = ButtonB(f"{i}", lambda x: print(f"hi from {x}"), text=f"Текст на кнопке {i}")
    #c = CentererB(10, 10)
    #c.add_child(button)
    bplacer.add_child(button)

placer.add_child(bplacer)
placer.add_child(TextInputB(), 0.1)
row_placer = RowPlacerB()

row_placer.add_child(ToggleButtonB("togglable", lambda name, state: print(name, state)), 0.1)
row_placer.add_child(TextInputB(callback=print))

placer.add_child(row_placer, 0.1)

pb = ProgressBarB()

placer.add_child(pb, 0.1)

centerer.add_child(placer)
#centerer.add_child(pb)

#win = Window()
#ctrl = WindowWidgetController()
#ctrl.set_window_node(win, centerer)
#ctrl.assign_to_window(win)
#rend = DefaultRenderer(win, centerer)

#while not win.should_close:
#    win.ctx.clear(0, 0, 0)
    #win.ctx.enable_only(moderngl.BLEND)
#    rend.render()
#    win.swap()
#    win.wait_events(0.05)
#    pb.fraction = (time.time()%10)/10
    #win.poll_events()
    #time.sleep(0.05)

app = App(centerer)

#app.rend.params["node_bg_color"] = (1, 1, 1, 0.5)

while not app.should_close:
    app.render()
    #win.wait_events()

#Just for tests
#ctrl.unassign_from_window(win)