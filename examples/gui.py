"""
  Example showing basically everything of widgets
"""

from qlibs.gui.widgets.behaviors import *
from qlibs.gui.widgets.app import App
from qlibs.highlevel.graphics import SpriteMaster


import time
import moderngl

centerer = CentererB(100, 100)
centerer.image_id = "eye"
centerer.image_mode = "fill"
centerer.image_ratio = 1 #y / x

placer = ColumnPlacerB()
#placer.spc = 20
'''
bplacer = ScrollableListB()
for i in range(20):
    button = ButtonB(f"{i}", lambda x: print(f"hi from {x}"), text=f"Text on button {i}")
    bplacer.add_child(button)
'''
bplacer = ScrollableStringListB(callback=print)
for i in range(20):
    bplacer.add_child(f"Text on button {i}")
    

placer.add_child(bplacer)
placer.add_child(TextInputB(), 0.1)
placer.add_child(TextNodeB("lalalalalalal sdfad asdf asdfas dfasdf sadf asdfasd fsadf sadf asdf adsf asdf das asd"))
row_placer = RowPlacerB()

row_placer.add_child(ToggleButtonB("togglable", lambda name, state: print(name, state)), 1)
b2 = ToggleButtonB("togglable", lambda name, state: print(name, state))
b2.image_id = "eye"
row_placer.add_child(b2, 1)
row_placer.add_child(TextInputB(callback=print))
    
row_placer.size_hint_func = hint_func_rel #Use hint function to make some widgets square


placer.add_child(row_placer, 0.1)

pb = ProgressBarB()

placer.add_child(pb, 0.1)

centerer.add_child(placer)

app = App(centerer)

spritem = SpriteMaster(app.ctx)
spritem.load_file("eye", "qlibs/images/eye.png")
spritem.init()

app.rend.sprite_master = spritem
#app.rend.excludes.pop(0)
#app.rend.params["node_bg_color"] = (1, 1, 1, 0.5)

stime = time.time()
ttime = 10

while not app.should_close:
    app.render(wait_time=0.1)
    ptime = time.time() - stime
    pb.fraction = (ptime % ttime) / ttime
