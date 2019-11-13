from qlibs.gui.widgets.behaviors import *
from qlibs.gui.widgets.app import App
from qlibs.highlevel.graphics import SpriteMaster

import time
import moderngl



centerer = CentererB(100, 100)
centerer.image_id = "eye"
centerer.image_mode = "fill"
centerer.image_ratio = 1

placer = ColumnPlacerB()
#placer.spc = 20
bplacer = ScrollableListB()
for i in range(20):
    button = ButtonB(f"{i}", lambda x: print(f"hi from {x}"), text=f"Текст на кнопке {i}")
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


app = App(centerer)

spritem = SpriteMaster(app.ctx)
spritem.load_file("eye", "qlibs/images/eye.png")
spritem.init()

app.rend.sprite_master = spritem
app.rend.excludes.clear()
#app.rend.params["node_bg_color"] = (1, 1, 1, 0.5)

while not app.should_close:
    app.render(wait_time=0.1)
    pb.fraction = (time.time()%10)/10
    #win.wait_events()

#Just for tests
#ctrl.unassign_from_window(win)